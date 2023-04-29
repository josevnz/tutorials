#!/bin/bash

declare -a submodules
submodules=(
"home_nmap"
"kismet_home"
"BashError"
"InteractiveBashScript"
"DatesAndComplexInBash"
"BashResources"
"rpm_query"
"EnableSysadminRssReader"
"ExtendingAnsibleWithPython"
"grafana"
"insecure_protocol_tutorial"
"influxdb_intro"
"influxdb_datasets"
"OracleCloudHomeLab"
"SuricataLog"
"yafd"
"nyrr"
"Nexus3OnOrangePI"
"StopUsingTelnetToTestPorts"
"BashHere"
"DebuggingApplications"
"Covid19Informer"
"Falco"
"linktester"
)

for module in ${submodules[*]}; do
	if [[ ! -d $module ]]; then
	    git submodule add "https://github.com/josevnz/${module}.git"
  fi
  echo "[$module]($module/README.md)"
done
