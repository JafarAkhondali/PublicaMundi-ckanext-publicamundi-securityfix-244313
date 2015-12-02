from ckanext.publicamundi.analytics.controllers.parsers.haparser import HAParser
from ckanext.publicamundi.analytics.controllers.parsedinfo.hausedcoveragesinfo import HAUsedCoveragesInfo


class HAUsedCoveragesParser(HAParser):
    """
    Specialized HAParser for information about the coverages that have been accessed.
    Limitations: currently works for WCS and WMS only.
    """
    __author__ = "<a href='mailto:merticariu@rasdaman.com'>Vlad Merticariu</a>"

    def __init__(self, log_lines):
        """
        Class constructor.
        :param list[str] log_lines: a list of log lines
        """
        HAParser.__init__(self, log_lines)

    def extract_coverage_names(self, separator, line):
        """
        Extracts the coverage names from a string.
        :param <string> separator: the token used to separate coverage names.
        :param <string> line: the log line from which the names are to be extracted.
        :return: <[string]> the list of coverage names found in the line.
        """
        coverage_names = []
        if separator in line:
            split = line.split(separator)
            # check if we are at the end of the request
            if self.and_key in split[1]:
                coverage_names_container = split[1].split(self.and_key)[0]
            else:
                coverage_names_container = split[1].split(" ")[0]
            # split the coverage_names_container, in case it contains more than 1 cov
            if self.coverage_separator_standard in coverage_names_container:
                coverage_names = coverage_names_container.split(self.coverage_separator_standard)
            elif self.coverage_separator_geoserver in coverage_names_container:
                coverage_names = [coverage_names_container.split(self.coverage_separator_geoserver)[1]]
            else:
                # single coverage given
                coverage_names = [coverage_names_container]
        return coverage_names

    def parse_line(self, line, accessed_coverages):
        """
        Parses a log line, extracting information about the coverages accessed in the line.
         :param <string> line: the log line to be parsed.
         :return: <[HAUsedCoveragesInfo]> a list of objects describing the coverages accessed in this line.
        """
        ret = []
        for coverage_name in accessed_coverages:
            if coverage_name.lower() in line:
                ret.append(HAUsedCoveragesInfo(HAParser.parse_date(line), coverage_name, 1))
        return ret

    def parse_accessed_coverages_line(self, line):
        accessed_coverages = []
        # look for a coverage or a layer in the line
        if self.wcs_coverage_access_key in line:
            accessed_coverages += self.extract_coverage_names(self.wcs_coverage_access_key, line)
        if self.wms_layers_access_key in line:
            accessed_coverages += self.extract_coverage_names(self.wms_layers_access_key, line)
        if self.wms_layer_access_key in line:
            accessed_coverages += self.extract_coverage_names(self.wms_layer_access_key, line)
        return accessed_coverages

    def parse(self):
        """
        Parses the current log file and extracts information about the coverages/layers that are present in the logs. For
        each coverage/layer, an object describing the access count is returned.
        :return: <[HAUsedCoveragesInfo]> the list of objects describing the coverages that have been accessed, sorted in
        descending order by number of accesses.
        """
        result = []
        accessed_coverages = self.parse_accessed_coverages()
        for line in self.log_lines:
            validated_line = self.validate_line(line)
            result += self.parse_line(validated_line, accessed_coverages)
        result = self.merge_info_list(result, HAUsedCoveragesInfo.coverage_name_property_key)
        # sort the result by access_count
        result.sort(key=lambda x: x.access_count, reverse=True)
        return result

    def parse_accessed_coverages(self):
        result = []
        for line in self.log_lines:
            result += self.parse_accessed_coverages_line(line)
        coverages = set()
        for cov in result:
            stripped_cov = cov.strip(' \t\n\r')
            if stripped_cov != "":
                coverages.add(stripped_cov)
        return list(coverages)

    """
    Key definitions, to know what to look for in the log file.
    """
    wcs_coverage_access_key = "coverageid="
    wms_layers_access_key = "layers="
    wms_layer_access_key = "layer="
    coverage_separator_standard = ","
    coverage_separator_geoserver = ":"
    and_key = "&"
