param(
    $ResourceGroupName = "RG-202-ARM-Development",
    $AksName = "AKS-DAK-EU-ARM-Development-202-DAKApp"
)
SET REGISTRY=petereit.azurecr.io/eshop
docker-compose -f .\docker-compose.yml  -f .\docker-compose.override.yml  build
docker-compose -f .\docker-compose.yml  -f .\docker-compose.override.yml  push
. $PSScriptRoot\k8s\helm\deploy-all.ps1 -externalDns aks -aksName $AksName -aksRg $ResourceGroupName -imageTag dev
# .\k8s\helm\deploy-all.ps1 -externalDns aks -aksName "AKS-DAK-EU-ARM-Development-202-DAKApp" -aksRg "RG-202-ARM-Development" -imageTag dev -dockerUser "d845c1eb-5b10-4cd3-a748-e3138e125b68" -dockerPassword (Read-Host "Password for Docker user")