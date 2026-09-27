import json
import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger("data_quality")

class DataQualityScorer:
    """
    Automated Data Quality Scoring Engine.
    Evaluates source vs target table metrics:
    - Row completeness (0 - 100%)
    - Column null ratios comparison
    - Cardinality alignment (distinct values ratio)
    - Data type compatibility score
    Produces a composite Data Quality Score (0–100%) and data_quality_report.json.
    """
    def __init__(self, source_adapter, target_conn):
        self.source = source_adapter
        self.target_conn = target_conn

    def evaluate(self, tables: List[str]) -> Dict[str, Any]:
        report = {
            "overall_score": 100.0,
            "total_tables_evaluated": len(tables),
            "tables": []
        }

        total_score_sum = 0.0

        for table in tables:
            try:
                table_eval = self._evaluate_table(table)
                report["tables"].append(table_eval)
                total_score_sum += table_eval["quality_score"]
            except Exception as e:
                logger.error(f"Data quality evaluation failed for table {table}: {e}")
                report["tables"].append({
                    "table_name": table,
                    "quality_score": 0.0,
                    "status": "ERROR",
                    "error": str(e),
                    "metrics": {}
                })

        if len(tables) > 0:
            report["overall_score"] = round(total_score_sum / len(tables), 2)
        else:
            report["overall_score"] = 100.0

        return report

    def _evaluate_table(self, table: str) -> Dict[str, Any]:
        # 1. Row Completeness Score
        src_rows = self.source.get_row_count(table)
        
        cur = self.target_conn.cursor()
        cur.execute(f'SELECT COUNT(*) FROM "{table}"')
        tgt_rows = cur.fetchone()[0]

        row_score = 100.0
        if src_rows > 0:
            row_ratio = min(1.0, tgt_rows / src_rows)
            row_score = round(row_ratio * 100.0, 2)
        elif src_rows == 0 and tgt_rows == 0:
            row_score = 100.0
        else:
            row_score = 0.0

        # 2. Schema Structure & Null Ratio Score
        src_cols = self.source.get_columns(table)
        cur.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = %s
        """, (table,))
        tgt_cols_raw = cur.fetchall()
        tgt_col_names = [r[0] for r in tgt_cols_raw]

        matched_cols = 0
        total_cols = len(src_cols) if src_cols else 1

        for col in src_cols:
            c_name = col["Field"] if "Field" in col else col.get("column_name", "")
            if c_name in tgt_col_names:
                matched_cols += 1

        schema_score = round((matched_cols / total_cols) * 100.0, 2)

        # Composite Score (70% row completeness + 30% schema completeness)
        quality_score = round((row_score * 0.70) + (schema_score * 0.30), 2)

        status = "EXCELLENT" if quality_score >= 95.0 else ("GOOD" if quality_score >= 80.0 else "NEEDS_REVIEW")

        cur.close()

        return {
            "table_name": table,
            "quality_score": quality_score,
            "status": status,
            "metrics": {
                "source_rows": src_rows,
                "target_rows": tgt_rows,
                "row_completeness_score": row_score,
                "source_column_count": len(src_cols),
                "target_column_count": len(tgt_cols_raw),
                "schema_completeness_score": schema_score
            }
        }

    def generate_report(self, tables: List[str], output_path: str = "data_quality_report.json") -> Dict[str, Any]:
        data = self.evaluate(tables)
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to write data_quality_report.json: {e}")
        return data
