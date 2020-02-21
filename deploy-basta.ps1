function Set-Cluster{
    az account set -s DAK-EU-Development
    kubectl config use-context AKS-DAK-EU-ARM-Development-202-DAKApp2
}

function Start-Site{
    $baseUrl = kubectl get ing eshop-identity-api -o=jsonpath='{.spec.rules[0].host}'
    Start-Process "http://$baseUrl/"
    Start-Process "http://$baseUrl/webstatus/hc-ui#/healthchecks"
}
function Build-All{
    Set-Cluster
    param($Path = "D:\dev\basta\eShopOnContainers")
    pushd
    cd "$Path\src"
    $env:REGISTRY = "jpetereit/eshop-"
    docker-compose build
    docker images --format "{{.Repository}}" | grep jpetereit/eshop- | %{ docker push $_ }
    cd "$Path\deploy\k8s\helm"
    .\deploy-all.ps1 -externalDns aks -aksName "AKS-DAK-EU-ARM-Development-202-DAKApp2" -aksRg "RG-202-ARM-Development" -imageTag linux-latest -useMesh $false -registry "jpetereit"

    kubectl apply -f aks-httpaddon-cfg.yaml
    kubectl delete pod $(kubectl get pod -l app=addon-http-application-routing-nginx-ingress -n kube-system -o jsonpath="{.items[0].metadata.name}") -n kube-system
    popd
}
function Build-Identity {
    Set-Cluster
    param($Path = "D:\dev\basta\eShopOnContainers\src")
    pushd
    cd $Path
    docker build . -f Services\Identity\Identity.API\Dockerfile -t "jpetereit/eshop-identity.api:linux-latest"
    docker push jpetereit/eshop-identity.api:linux-latest
    kubectl get pods -o=name |grep eshop-identity-api |%{ kubectl delete $_}
    Start-Sleep -Seconds 1
    
    kubectl get pods -o=name |grep eshop-identity-api |%{kubectl logs -f $_}
    popd
}


<#
cd "D:\dev\basta\eShopOnContainers\deploy\k8s\helm"
kubectl create clusterrolebinding kubernetes-dashboard -n kube-system --clusterrole=cluster-admin --serviceaccount=kube-system:kubernetes-dashboard
#>

# .\deploy-all.ps1 -externalDns aks -aksName "AKS-DAK-EU-ARM-Development-202-DAKApp2" -aksRg "RG-202-ARM-Development" -imageTag dev -useMesh $false

# allow large headers
function Generate-Users{
    param(
        $Path = "D:\dev\basta\eShopOnContainers",
        $count = 500
    )
    pushd
    cd "$Path\src\Tests\Tools\UserFileGenerator"
    dotnet publish -r win-x64 -c release
    cd "$Path\src\Tests\Tools\UserFileGenerator\bin\release\netcoreapp3.1\win-x64\publish"
    UserFileGenerator.exe $count > "$Path\src\Services\Identity\Identity.API\Setup\Users.csv"
    popd
    
}
function Build-Locust{
    param(
        $Path = "D:\dev\basta\eShopOnContainers",
        [switch]$Interactive
    )
    pushd
    $target = "$Path\locust\helm\stable\locust\tasks"
    cp "$Path\src\Services\Identity\Identity.API\Setup\Users.csv" $target
    cp "$Path\locust\*.py" $target
    if ($Interactive.IsPresent) {
        python "$target\locustfile.py" -i
    }
    else{
        $baseUrl = kubectl get ing eshop-identity-api -o=jsonpath='{.spec.rules[0].host}'
        helm upgrade --install locust-nymph --set master.config.target-host="http://$baseUrl" "$path\locust\helm\stable\locust" -f "$path\locust\values.yaml" --set "ingress.hosts={$baseUrl}"
    }
    popd
}
