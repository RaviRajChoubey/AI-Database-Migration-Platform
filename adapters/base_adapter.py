class BaseAdapter:

    def get_tables(self):
        raise NotImplementedError

    def get_columns(self, table):
        raise NotImplementedError

    def get_indexes(self, table):
        raise NotImplementedError

    def get_foreign_keys(self, table):
        raise NotImplementedError

    def get_views(self):
        raise NotImplementedError

    def get_triggers(self):
        raise NotImplementedError

    def get_functions(self):
        raise NotImplementedError

    def get_procedures(self):
        raise NotImplementedError

    def get_check_constraints(self, table):
        raise NotImplementedError

    def get_default_values(self, table):
        raise NotImplementedError

    def get_unique_constraints(self, table):
        raise NotImplementedError
    
    def get_connection(self):
        pass