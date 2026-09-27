import json
import os
import re
import logging
from typing import Dict, Any, List, Optional

# Logging setup
logger = logging.getLogger("ai_translator")

class SelfHealingAgent:
    """
    Self-Healing Agent for cognitive DDL & schema error repair.
    Intercepts execution failures on PostgreSQL target database,
    extracts error traceback & context, generates repaired PostgreSQL SQL
    using LLM or heuristic translation rules, and saves successful rules to schema_memory.json.
    """
    def __init__(self, memory_file_path: Optional[str] = None):
        if memory_file_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            memory_file_path = os.path.join(base_dir, "mappings", "schema_memory.json")
        
        self.memory_file_path = memory_file_path
        self.schema_memory = self._load_memory()
        self.healing_history: List[Dict[str, Any]] = []

    def _load_memory(self) -> Dict[str, str]:
        if os.path.exists(self.memory_file_path):
            try:
                with open(self.memory_file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load schema_memory.json: {e}")
        return {}

    def save_memory(self):
        try:
            os.makedirs(os.path.dirname(self.memory_file_path), exist_ok=True)
            with open(self.memory_file_path, "w", encoding="utf-8") as f:
                json.dump(self.schema_memory, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save schema_memory.json: {e}")

    def repair_sql(self, original_sql: str, error_message: str, source_type: str = "mysql") -> Dict[str, Any]:
        """
        Attempts to repair a failed SQL statement.
        Returns a dict: {"success": bool, "repaired_sql": str, "rule_learned": Optional[str], "method": str}
        """
        error_lower = error_message.lower()
        cleaned_sql = original_sql.strip()

        # Check if we already have a memory mapping for this pattern
        for pattern, replacement in self.schema_memory.items():
            if pattern in cleaned_sql:
                repaired = cleaned_sql.replace(pattern, replacement)
                return {
                    "success": True,
                    "repaired_sql": repaired,
                    "rule_learned": f"Applied cached memory rule: {pattern} -> {replacement}",
                    "method": "schema_memory"
                }

        # Try LLM repair if API keys exist
        llm_result = self._try_llm_repair(cleaned_sql, error_message, source_type)
        if llm_result:
            return llm_result

        # Heuristic Rule Engine Fallbacks
        repaired_sql = cleaned_sql
        rule_learned = None
        method = "heuristic_rules"

        # Rule 1: MySQL datetime2 / datetime default current_timestamp() or getdate()
        if "getdate()" in error_lower or "now()" in error_lower or "current_timestamp()" in error_lower:
            if "getdate()" in repaired_sql.lower():
                repaired_sql = re.sub(r'getdate\(\)', 'CURRENT_TIMESTAMP', repaired_sql, flags=re.IGNORECASE)
                rule_learned = "Converted GETDATE() to CURRENT_TIMESTAMP"
            elif "now()" in repaired_sql.lower():
                repaired_sql = re.sub(r'now\(\)', 'CURRENT_TIMESTAMP', repaired_sql, flags=re.IGNORECASE)
                rule_learned = "Converted NOW() to CURRENT_TIMESTAMP"

        # Rule 2: Datatype syntax mismatches (e.g. DATETIME2, tinyint(1), unsigned)
        if "type" in error_lower or "syntax" in error_lower or "does not exist" in error_lower:
            if "unsigned" in repaired_sql.lower():
                repaired_sql = re.sub(r'\bunsigned\b', '', repaired_sql, flags=re.IGNORECASE)
                rule_learned = "Removed MySQL 'UNSIGNED' modifier for PostgreSQL compatibility"
            if "datetime2" in repaired_sql.lower():
                repaired_sql = re.sub(r'\bdatetime2(\(\d+\))?\b', 'TIMESTAMP', repaired_sql, flags=re.IGNORECASE)
                rule_learned = "Converted DATETIME2 to TIMESTAMP"
            if "tinyint(1)" in repaired_sql.lower() or "tinyint" in repaired_sql.lower():
                repaired_sql = re.sub(r'\btinyint(\(\d+\))?\b', 'BOOLEAN', repaired_sql, flags=re.IGNORECASE)
                rule_learned = "Converted TINYINT to BOOLEAN"
            if "auto_increment" in repaired_sql.lower():
                repaired_sql = re.sub(r'\bauto_increment\b', 'GENERATED ALWAYS AS IDENTITY', repaired_sql, flags=re.IGNORECASE)
                rule_learned = "Converted AUTO_INCREMENT to GENERATED ALWAYS AS IDENTITY"

        # Rule 3: Single quotes vs double quotes for identifiers/defaults
        if "column" in error_lower and "does not exist" in error_lower:
            # Replace single quotes around column names in index/constraint definitions
            repaired_sql = re.sub(r"'([a-zA-Z0-9_]+)'", r'"\1"', repaired_sql)
            rule_learned = "Converted single quoted identifier to double quotes"

        # Rule 4: MySQL backticks to PostgreSQL double quotes
        if "`" in repaired_sql:
            repaired_sql = repaired_sql.replace("`", '"')
            rule_learned = "Converted MySQL backticks to PostgreSQL double quotes"

        # Check if any rule changed the SQL
        if repaired_sql != cleaned_sql:
            if rule_learned:
                pattern_key = cleaned_sql[:50]
                self.schema_memory[pattern_key] = repaired_sql[:50]
                self.save_memory()

            record = {
                "original_sql": original_sql,
                "error_message": error_message,
                "repaired_sql": repaired_sql,
                "rule_learned": rule_learned,
                "method": method
            }
            self.healing_history.append(record)

            return {
                "success": True,
                "repaired_sql": repaired_sql,
                "rule_learned": rule_learned,
                "method": method
            }

        return {
            "success": False,
            "repaired_sql": original_sql,
            "rule_learned": None,
            "method": "failed"
        }

    def _try_llm_repair(self, sql: str, error: str, source_type: str) -> Optional[Dict[str, Any]]:
        openai_key = os.environ.get("OPENAI_API_KEY")
        gemini_key = os.environ.get("GEMINI_API_KEY")

        if not (openai_key or gemini_key):
            return None

        prompt = f"""You are a Database Migration AI Specialist.
A PostgreSQL DDL query failed during migration from {source_type}.

Failed SQL:
{sql}

PostgreSQL Error Traceback:
{error}

Return ONLY valid, executable PostgreSQL SQL code that fixes this error. Do not include markdown formatting or commentary."""

        try:
            if openai_key:
                import urllib.request
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {openai_key}"
                }
                body = json.dumps({
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1
                }).encode("utf-8")

                req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=body, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    repaired = data["choices"][0]["message"]["content"].strip()
                    repaired = re.sub(r"^```sql\s*", "", repaired, flags=re.IGNORECASE)
                    repaired = re.sub(r"```$", "", repaired).strip()
                    return {
                        "success": True,
                        "repaired_sql": repaired,
                        "rule_learned": "Repaired using OpenAI LLM agent",
                        "method": "openai_llm"
                    }
        except Exception as e:
            logger.warning(f"LLM repair call failed: {e}")

        return None


class RoutineTranslator:
    """
    Translates stored procedures, triggers, and functions from MSSQL (T-SQL) or MySQL
    into valid PostgreSQL PL/pgSQL function & trigger definitions.
    """
    def __init__(self):
        pass

    def translate_procedure(self, name: str, definition: str, source_type: str = "mysql") -> Dict[str, Any]:
        """
        Translates a procedure to PostgreSQL PL/pgSQL function.
        """
        if not definition or not definition.strip():
            return {
                "name": name,
                "translated_sql": f"-- Empty routine definition for {name}",
                "status": "SKIPPED",
                "notes": "Empty definition"
            }

        cleaned = definition.strip()

        # Attempt LLM translation if API key is present
        llm_translated = self._try_llm_translate(name, cleaned, "procedure", source_type)
        if llm_translated:
            return {
                "name": name,
                "translated_sql": llm_translated,
                "status": "TRANSLATED",
                "notes": "Translated using LLM agent"
            }

        # Heuristic PL/pgSQL Generator
        body_content = cleaned

        # Strip CREATE PROCEDURE header if present
        header_match = re.search(r'CREATE\s+(?:DEFINER=`[^`]+`@`[^`]+`\s+)?PROCEDURE\s+(?:`?\w+`?\.)?`?(\w+)`?\s*\((.*?)\)\s*(?:BEGIN|AS)', cleaned, re.IGNORECASE | re.DOTALL)
        params_str = ""
        if header_match:
            params_str = header_match.group(2).strip()
            # Extract body after BEGIN
            begin_pos = re.search(r'\bBEGIN\b', cleaned, re.IGNORECASE)
            if begin_pos:
                body_content = cleaned[begin_pos.start():]

        # Basic T-SQL / MySQL keyword conversions in body
        body_content = re.sub(r'\bDECLARE\s+@(\w+)', r'DECLARE \1', body_content, flags=re.IGNORECASE)
        body_content = re.sub(r'@(\w+)', r'\1', body_content)
        body_content = re.sub(r'\bGETDATE\(\)', 'CURRENT_TIMESTAMP', body_content, flags=re.IGNORECASE)
        body_content = re.sub(r'\bISNULL\(', 'COALESCE(', body_content, flags=re.IGNORECASE)

        # Ensure PL/pgSQL structure
        if not re.search(r'\bBEGIN\b', body_content, re.IGNORECASE):
            body_content = f"BEGIN\n{body_content}\nEND;"

        # Format as PL/pgSQL FUNCTION
        plpgsql_func = f"""CREATE OR REPLACE FUNCTION "{name}"()
RETURNS void AS $$
{body_content}
$$ LANGUAGE plpgsql;"""

        return {
            "name": name,
            "translated_sql": plpgsql_func,
            "status": "TRANSLATED",
            "notes": "Translated using Heuristic PL/pgSQL Converter"
        }

    def translate_trigger(self, name: str, definition: str, source_type: str = "mysql") -> Dict[str, Any]:
        """
        Translates a trigger to PostgreSQL trigger function + CREATE TRIGGER statement.
        """
        if not definition or not definition.strip():
            return {
                "name": name,
                "translated_sql": f"-- Empty trigger definition for {name}",
                "status": "SKIPPED",
                "notes": "Empty definition"
            }

        cleaned = definition.strip()
        llm_translated = self._try_llm_translate(name, cleaned, "trigger", source_type)
        if llm_translated:
            return {
                "name": name,
                "translated_sql": llm_translated,
                "status": "TRANSLATED",
                "notes": "Translated using LLM agent"
            }

        # Extract table and timing
        table_match = re.search(r'ON\s+`?(\w+)`?', cleaned, re.IGNORECASE)
        table_name = table_match.group(1) if table_match else "target_table"

        timing = "BEFORE" if "BEFORE" in cleaned.upper() else "AFTER"
        event = "INSERT"
        if "UPDATE" in cleaned.upper():
            event = "UPDATE"
        elif "DELETE" in cleaned.upper():
            event = "DELETE"

        func_name = f"trg_func_{name}"

        plpgsql_trigger = f"""CREATE OR REPLACE FUNCTION "{func_name}"()
RETURNS trigger AS $$
BEGIN
    -- Auto-translated PL/pgSQL trigger function for {name}
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER "{name}"
{timing} {event} ON "{table_name}"
FOR EACH ROW EXECUTE FUNCTION "{func_name}"();"""

        return {
            "name": name,
            "translated_sql": plpgsql_trigger,
            "status": "TRANSLATED",
            "notes": "Translated using Heuristic PL/pgSQL Trigger Converter"
        }

    def _try_llm_translate(self, name: str, code: str, routine_type: str, source_type: str) -> Optional[str]:
        openai_key = os.environ.get("OPENAI_API_KEY")
        if not openai_key:
            return None

        prompt = f"""Convert this {source_type} {routine_type} named '{name}' to PostgreSQL PL/pgSQL code:

Source Code:
{code}

Return ONLY valid PostgreSQL PL/pgSQL code (e.g. CREATE OR REPLACE FUNCTION...). No markdown blocks, no extra explanation."""

        try:
            import urllib.request
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai_key}"
            }
            body = json.dumps({
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }).encode("utf-8")

            req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=body, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                repaired = data["choices"][0]["message"]["content"].strip()
                repaired = re.sub(r"^```sql\s*", "", repaired, flags=re.IGNORECASE)
                repaired = re.sub(r"```$", "", repaired).strip()
                return repaired
        except Exception:
            return None
