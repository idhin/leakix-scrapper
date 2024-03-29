import sys
import json
import time
import requests
import argparse
from os.path import exists
from rich.console import Console


parser = argparse.ArgumentParser()
parser.add_argument(
    "-s", "--scope", choices=["service", "leak"], help="Type Of Informations"
)
parser.add_argument("-p", "--pages", help="Number Of Pages", default="2")
parser.add_argument("-q", "--query", help="Specify The Query", default="")
parser.add_argument("-P", "--plugin", help="Specify The Plugin")
parser.add_argument("-o", "--output", help="Output File")
args = parser.parse_args()

console = Console()


api_key_file = ".api.txt"


def get_plugins():
    plugins = [
        "ApacheStatusHttpPlugin",
        "BitbucketPlugin",
        "CheckMkPlugin" "CiscoRV",
        "ConfigJsonHttp",
        "ConfluenceVersionIssue",
        "Consul",
        "CouchDbOpenPlugin" "DeadMon",
        "DockerRegistryHttpPlugin",
        "DotDsStoreOpenPlugin",
        "DotEnvConfigPlugin",
        "ElasticSearchOpenPlugin",
        "ExchangeVersion",
        "GitConfigHttpPlugin",
        "GrafanaOpenPlugin",
        "HiSiliconDVR",
        "HttpNTLM",
        "JenkinsOpenPlugin",
        "JiraPlugin",
        "KafkaOpenPlugin",
        "LaravelTelescopeHttpPlugin",
        "Log4JOpportunistic",
        "MetabaseHttpPlugin",
        "MongoOpenPlugin",
        "MysqlOpenPlugin",
        "PaloAltoPlugin",
        "PhpInfoHttpPlugin",
        "PhpStdinPlugin",
        "ProxyOpenPlugin",
        "QnapVersion",
        "RedisOpenPlugin",
        "SmbPlugin",
        "SonarQubePlugin",
        "SonicWallSMAPlugin",
        "SophosPlugin",
        "SymfonyProfilerPlugin",
        "SymfonyVerbosePlugin",
        "TraversalHttpPlugin",
        "veeaml9",
        "WpUserEnumHttp",
        "YiiDebugPlugin",
        "ZimbraPlugin",
        "ZookeeperOpenPlugin",
        "ZyxelVersion",
    ]
    return plugins


def check_output(result):
    if args.output and len(result) != 0:
        with open(args.output, "w") as f:
            result = list(dict.fromkeys(result))
            for line in result:
                f.write(f"{line}\n")
        console.print(
            f"\n[bold green][+] File written successfully to {args.output} with {len(result)} lines\n"
        )
    sys.exit(0)


def main():

    plugins = get_plugins()

    if args.plugin:
        if args.plugin in plugins:
            args.query = f"+plugin:{args.plugin}"
        else:
            console.print("\n[bold red][X] Plugin is not valid")
            console.print(f"[bold yellow][!] Plugins available : {len(plugins)}\n")
            for plugin in plugins:
                console.print(f"[bold cyan][+] {plugin}")
            print()
            sys.exit(1)

    api_file = exists(api_key_file)

    try:
        api_key = open(api_key_file, "r").read().strip()

    except:
        api_key = list()

    if not api_file and len(api_key) == 0:
        api_key = input(
            "Please Specify your API Key (leave blank if you don't have) : "
        )
        with open(api_key_file, "w") as f:
            f.write(api_key)

    if len(api_key) == 0:
        console.print(
            f"\n[bold yellow][!] Querying without API Key...\n (remove or edit {api_key_file} to add API Key if you have)"
        )

    else:
        console.print("\n[bold green][+] Using API Key for queries...\n")

    result = list()
    tmp = list()
    for page in range(0, int(args.pages)):

        headers = {
            "api-key": f"{api_key}",
            "Accept": "application/json",
        }

        params = {
            "page": f"{page}",
            "q": f"{args.query}",
            "scope": f"{args.scope}",
        }

        response = requests.get(
            "https://leakix.net/search", params=params, headers=headers
        )

        if response.text == "null":
            console.print(
                "[bold yellow][!] No results available (Please check your query or scope)"
            )
            check_output(result)
            break

        elif response.text == '{"Error":"Page limit"}':
            console.print(
                f"[bold red][X] Error : Page Limit for free users and non users ({page})"
            )
            check_output(result)
            break

        else:
            console.print(f"[bold green] Query {page + 1} : \n")
            data = json.loads(response.text)

            try:
                exist = data[1]["protocol"]
            except:
                console.print(
                    f"[bold red][X] Error : You're not allowed to use this plugin ({args.plugin})\n"
                )
                check_output(result)
                break
            try:
                for json_data in range(1, len(data)):
                    protocol = f"{data[json_data]['protocol']}://"
                    protocol = (
                        protocol
                        if protocol == "http://" or protocol == "https://"
                        else ""
                    )
                    ip = data[json_data]["ip"]
                    port = data[json_data]["port"]
                    target = f"{protocol}{ip}:{port}"
                    tmp_result = tmp.append(target)

                tmp = list(dict.fromkeys(tmp))
                for tmp_target in tmp:
                    console.print(f"[bold blue][+] {tmp_target}")
                    result_prompt = result.append(tmp_target)
            except:
                pass

            tmp.clear()

        console.print("\n")
        time.sleep(1.9)

    check_output(result)


if __name__ == "__main__":
    main()

