#!/usr/local/autopkg/python
#
# Copyright 2024 Justin Holt (jholt13)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

from autopkglib import ProcessorError, URLGetter

__all__ = ["CraftingSandboxURLProvider"]


class CraftingSandboxURLProvider(URLGetter):

    """This processor finds the download URL and version for the Crafting
    Sandbox CLI tool."""

    description = __doc__
    input_variables = {
        "download_arch": {
            "required": False,
            "default": "amd64",
            "description": (
                "Processor download_arch for which to package cs binary (amd64 or arm64)"
                "Default download_arch: amd64"
            )
        },
        "os_type": {
            "required": False,
            "default": "darwin",
            "description": (
                "Operating system for which to package cs binary (darwin or linux)"
                "Default Operating System: darwin"
            )
        },
    }
    output_variables = {
        "download_url": {"description": "Returns the url to download."},
        "version": {"description": "Returns the version of the package to download."}
    }


    def main(self):
        cli_base_url = "https://storage.googleapis.com/cloud-sandboxes/cs"
        version_url = f"{cli_base_url}/version.json"

        arch = self.env.get("download_arch")
        os_type = self.env.get("os_type")

        # Build the headers
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }

        # Build the required curl switches
        curl_opts = [
            "--url",
            f"{version_url}",
        ]

        try:
            # Initialize the curl_cmd, add the curl options, and execute curl
            curl_cmd = self.prepare_curl_cmd()
            self.add_curl_headers(curl_cmd, headers)
            curl_cmd.extend(curl_opts)
            response = self.download_with_curl(curl_cmd)

        except:
            raise ProcessorError("Failed to retrieve Crafting Sandbox version information!")

        try:
            # Load the JSON response
            json_data = json.loads(response)
            version = json_data["version"]
            folder = json_data["folder"]
            self.output(f"Version:  {version}, Folder:  {folder}", verbose_level=3)

        except:
            raise ProcessorError("Failed to parse the json response!")

        try:
            download_url = f"{cli_base_url}/{folder}/cs-{os_type}-{arch}.tar.gz"

            self.env["version"] = version
            self.env["download_url"] = download_url

            self.output(
                f"Crafting Sandbox version that will be downloaded: {self.env['version']}", verbose_level=1)
            self.output(f"Download URL:  {download_url}", verbose_level=3)

        except:
            raise ProcessorError("Something went wrong assigning environment variables!")


if __name__ == "__main__":
    processor = CraftingSandboxURLProvider()
    processor.execute_shell()