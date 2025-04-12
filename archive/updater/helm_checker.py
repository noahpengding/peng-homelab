import requests
import yaml
import string
from app.utils.log import output_log


class HelmChecker:
    def _get_helm_chart(self, chart_url) -> str:
        try:
            url = f"{chart_url}/index.yaml"
            r = requests.get(url)
            clean_text = "".join(c for c in r.text if c in string.printable)
            data = yaml.safe_load(clean_text)
            return data
        except Exception as e:
            output_log(f"Error in get helm charts: {e}", "error")
            return None

    def check_helm(self, chart_url, chart_name, current_version) -> bool:
        data = self._get_helm_chart(chart_url)
        try:
            chart_version = data["entries"][chart_name][0]["version"]
            return chart_version == current_version
        except Exception as e:
            output_log(f"Error in check helm with {chart_version}: {e}", "error")

    def pull_helm_version(self, chart_url, chart_name) -> list:
        data = self._get_helm_chart(chart_url)
        return data["entries"][chart_name][0]["version"]
