from prompt_toolkit.completion import Completion, Completer


class BQCompleter(Completer):

    def __init__(self, schema=None):
        self.words = {
            "keyword": sorted(set([
                "*", "all", "as", "asc", "by", "cross", "desc", "distinct", "except",
                "full", "from", "group", "having", "inner", "intersect", "join",
                "limit", "left", "offset", "order", "outer", "over", "partition",
                "qualify", "replace", "right", "select", "struct", "union",
                "unnest", "value", "where", "window", "with", "pivot", "unpivot",
                "tablesample", "is", "not", "true", "false", "and", "or", "like",
                "between", "exists", "case", "when", "coalesce", "if", "ifnull",
                "nullif", "update", "create", "table", "set", "values",
                "declare", "default", "insert", "into"
            ])),
            "type": sorted(set([
                "null", "geography", "string", "bool", "int64", "float64", "bytes",
                "array", "timestamp", "date", "time", "datetime", "numeric",
                "bignumeric", "decimal"
            ])),
            "function": sorted(set([
                "abs", "any_value", "array", "array_agg", "array_concat",
                "array_concat_agg", "array_length", "array_to_string",
                "avg", "bit_and", "bit_or", "bit_xor", "cast", "ceil",
                "corr", "count", "countif", "covar_pop", "covar_samp",
                "current_date", "date", "date_add", "date_diff", "date_sub",
                "date_trunc", "extract", "floor", "ln", "log", "log10",
                "logical_and", "logical_or", "max", "min", "rand", "round",
                "sign", "sqrt", "stddev_pop", "stddev_samp",
                "string_agg", "sum", "var_pop", "var_samp", "keys.new_keyset",
                "keys.add_key_from_raw_bytes", "aead.decrypt_bytes",
                "aead.decrypt_string", "aead.encrypt", "keys.keyset_from_json",
                "keyset.keyset_to_json", "keys.rotate_keyset", "keys.keyset_length",
                "approx_count_distinct", "approx_quantiles", "approx_top_count",
                "approx_top_sum", "generate_array", "generate_date_array",
                "generate_timestamp_array", "array_reverse", "offset", "ordinal",
                "safe_offset", "safe_ordinal", "bit_count", "safe_cast",
                "date_from_unix_date", "format_date", "last_day", "parse_date",
                "unix_date", "current_datetime", "datetime", "extract",
                "datetime_add", "datetime_sub", "datetime_diff", "datetime_trunc",
                "format_datetime", "parse_datetime", "error", "external_query",
                "st_area", "st_asbinary", "as_asgeojson", "st_astext", "st_boundary",
                "st_centroid", "st_centroid_agg", "st_closestpoint", "st_clusterdbscan",
                "st_contains", "st_convexhull", "st_coveredby", "st_covers",
                "st_difference", "st_dimension", "st_disjoint", "st_equals",
                "st_geogfromjson", "st_geogfromtext", "st_geogfromwkb", "st_geogpoint",
                "st_geogpointfromgeohash", "st_geohash", "st_intersection",
                "st_intersects", "st_intersectsbox", "st_isocollection",
                "st_isempty", "st_length", "st_makeline", "st_makepolygon",
                "st_makepolygonoriented", "st_maxdistance", "st_npoints",
                "st_numpoints", "st_perimeter", "st_pointn", "st_simplify",
                "st_snaptogrid", "st_startpoint", "st_touches", "st_union",
                "st_union_agg", "st_within", "st_x", "st_y",
                "farm_fingerprint", "md5", "sha1", "sha256", "sha512",
                "hll_count.init", "hll_count.merge", "hll_count.merge_partial",
                "hll_count.extract",
                "json_extract", "json_query", "json_extract_scalar", "json_value",
                "json_extract_array", "json_query_array", "json_extract_string_array",
                "json_value_array", "to_json_string", "sign", "is_inf", "is_nan",
                "ieee_divide", "rand", "sqrt", "pow", "power", "exp", "ln", "log",
                "log10", "greatest", "least", "div", "safe_divide", "safe_multiply",
                "safe_negate", "safe_add", "safe_subtract", "mod", "round", "trunc",
                "ceil", "ceiling", "floor", "cos", "cosh", "acos", "acosh", "sin",
                "sinh", "asin", "asinh", "tan", "tanh", "atan", "atanh", "atan2",
                "range_bucket", "first_value", "last_value", "nth_value", "lead",
                "lag", "percentile_cont", "percentile_disc", "net.ip_from_string",
                "net.safe_ip_from_string", "net.ip_to_string", "net.ip_net_mask",
                "net.ip_trunc", "net.ipv4_from_int64", "net.ipv4_to_int64",
                "net.host", "net.public_suffix", "net.reg_domain", "rank",
                "dense_rank", "percent_rank", "cume_dist", "ntile", "row_number",
                "session_user", "corr", "covar_pop", "covar_samp", "stddev_pop",
                "stddev_samp", "stddev", "var_pop", "var_samp", "variance", "ascii",
                "byte_length", "char_length", "character_length", "chr",
                "code_points_to_bytes", "code_points_to_string", "concat", "ends_with",
                "format", "from_base32", "from_base64", "from_hex", "initcap", "instr",
                "left", "length", "lpad", "lower", "ltrim", "normalize",
                "normalize_and_casefold", "octet_length", "regexp_contains",
                "regexp_extract", "regexp_extract_all", "regexp_instr",
                "regexp_replace", "regexp_substr", "replace", "repeat", "reverse",
                "right", "rpad", "rtrim", "safe_convert_btyes_to_string",
                "soundex", "split", "starts_with", "strpos", "substr", "substring",
                "to_base32", "to_base64", "to_code_points", "to_hex", "translate",
                "trim", "unicode", "upper", "current_time", "time", "extract",
                "time_add", "time_sub", "time_diff", "time_trunc", "format_time",
                "parse_time", "current_timestamp", "timestamp", "timestamp_add",
                "timestamp_sub", "timestamp_diff", "timestamp_trunc",
                "format_timestamp", "parse_timestamp", "timestamp_seconds",
                "timestamp_millis", "timestamp_micros", "unix_seconds",
                "unix_millis", "unix_micros", "generate_uuid",
            ])),
        }

        self.word_order = ["keyword", "type", "function"]

    def get_completions(self, document, complete_event):
        w = document.get_word_before_cursor().lower()
        sp = len(w)
        if sp:
            for key in self.word_order:
                for k in self.words.get(key):
                    if k.startswith(w):
                        if key == "function":
                            k += "()"
                        if key == "type":
                            k = k.upper()

                        yield Completion(k, display_meta=key, start_position=-sp)
