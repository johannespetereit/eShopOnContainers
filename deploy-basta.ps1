function Set-Cluster {
    param([ValidateSet('app', 'locust')]$app = 'app')
    if ($app -eq 'app') {
        az account set -s "Visual Studio Premium mit MSDN"
        kubectl config use-context aks-eshop-v2
    }
    else {
        az account set -s "DAK-EU-Development"
        kubectl config use-context AKS-DAK-EU-ARM-Development-202-DAKApp2
    }
}
function Start-Site {
    Set-Cluster
    $baseUrl = kubectl get ing eshop-identity-api -o=jsonpath='{.spec.rules[0].host}'
    Start-Process "http://$baseUrl/"
    Start-Process "http://$baseUrl/webstatus/hc-ui#/healthchecks"
}
function Build-All {
    param(
        $Path = "D:\dev\basta\eShopOnContainers",
        [switch]$Rebuild,
        [switch]$Clean
    )
    Set-Cluster
    pushd
    if ($Rebuild.IsPresent) {
        cd "$Path\src"
        $env:REGISTRY = "jpetereit/eshop-"
        docker-compose build
        docker images --format "{{.Repository}}" | grep jpetereit/eshop- | % { docker push $_ }
    }
    cd "$Path\deploy\k8s\helm"
    .\deploy-all.ps1 -externalDns aks -aksName "aks-eshop-v2" -aksRg "eshop-v2" -imageTag linux-latest -useMesh $false -registry "jpetereit" -clean $Clean.IsPresent

    kubectl apply -f aks-httpaddon-cfg.yaml
    kubectl delete pod $(kubectl get pod -l app=addon-http-application-routing-nginx-ingress -n kube-system -o jsonpath="{.items[0].metadata.name}") -n kube-system
    popd
}
function Build-Basket {
    param($Path = "D:\dev\basta\eShopOnContainers\src")
    Set-Cluster
    pushd
    cd $Path
    docker build . -f Services\Basket\Basket.API\Dockerfile -t "jpetereit/eshop-basket.api:linux-latest"
    docker push jpetereit/eshop-basket.api:linux-latest
    kubectl get pods -o=name | grep eshop-basket-api | % { kubectl delete $_ }
    Start-Sleep -Seconds 2
    
    kubectl get pods -o=name | grep eshop-basket-api | % { kubectl logs -f $_ }
    popd
}

function Build-Catalog {
    param($Path = "D:\dev\basta\eShopOnContainers\src")
    Set-Cluster
    pushd
    cd $Path
    docker build . -f Services\Catalog\Catalog.API\Dockerfile -t "jpetereit/eshop-catalog.api:linux-latest"
    docker push jpetereit/eshop-catalog.api:linux-latest
    kubectl get pods -o=name | grep eshop-catalog-api | % { kubectl delete $_ }
    Start-Sleep -Seconds 2
    
    kubectl get pods -o=name | grep eshop-catalog-api | % { kubectl logs -f $_ }
    popd
}
function Build-Identity {
    param($Path = "D:\dev\basta\eShopOnContainers\src")
    Set-Cluster
    pushd
    cd $Path
    docker build . -f Services\Identity\Identity.API\Dockerfile -t "jpetereit/eshop-identity.api:linux-latest"
    docker push jpetereit/eshop-identity.api:linux-latest
    kubectl get pods -o=name | grep eshop-identity-api | % { kubectl delete $_ }
    Start-Sleep -Seconds 2
    
    kubectl get pods -o=name | grep eshop-identity-api | % { kubectl logs -f $_ }
    popd
}

function Build-ApiGW {
    param($Path = "D:\dev\basta\eShopOnContainers\src")
    Set-Cluster
    pushd
    cd $Path
    docker build . -f ApiGateways\Web.Bff.Shopping\aggregator\Dockerfile -t "jpetereit/eshop-webshoppingagg:linux-latest"
    docker push jpetereit/eshop-webshoppingagg:linux-latest
    kubectl get pods -o=name | grep eshop-webshoppingagg | % { kubectl delete $_ }
    Start-Sleep -Seconds 2
    
    kubectl get pods -o=name | grep eshop-webshoppingagg | % { kubectl logs -f $_ }
    popd
}

function Generate-Users {
    param(
        $Path = "D:\dev\basta\eShopOnContainers",
        $count = 500
    )
    pushd
    cd "$Path\src\Tests\Tools\UserFileGenerator"
    dotnet publish -r win-x64 -c release
    cd "$Path\src\Tests\Tools\UserFileGenerator\bin\release\netcoreapp3.1\win-x64\publish"
    $users = @(.\UserFileGenerator.exe $count)
    [IO.File]::WriteAllLines("$Path\src\Services\Identity\Identity.API\Setup\Users.csv", ($users | ? { $_.Trim() -ne "" } ))
    popd
    
}
function Build-Locust {
    param(
        $Path = "D:\dev\basta\eShopOnContainers",
        [switch]$Interactive,
        [switch]$Restart
    )
    pushd
    $target = "$Path\locust\locust-ingress\tasks"
    cp "$Path\src\Services\Identity\Identity.API\Setup\Users.csv" $target
    cp "$Path\locust\*.py" $target
    if ($Interactive.IsPresent) {
        python "$target\locustfile.py" -i
    }
    else {
        Set-Cluster -app app
        $baseUrl = kubectl get ing eshop-identity-api -o=jsonpath='{.spec.rules[0].host}'
        Set-Cluster -app locust
        helm upgrade --install locust --set locust.master.config.target-host="http://$baseUrl" "$path\locust\locust-ingress" -f "$path\locust\locust-ingress\values.yaml" --set "ingress.hosts={}"
    }
    if ($Restart.IsPresent) {
        $Pods = kubectl get pods -o=name; $pods | % { kubectl delete  $_ }
    }
    # kubectl get pods -n kube-system -o=name | grep addon-http-application-routing
    Start-Sleep -Seconds 60
    Invoke-WebRequest -Method Post -Uri http://104.40.231.150/locust/swarm -Body "locust_count=400&hatch_rate=10&host=http%3A%2F%2Feshop.5f925ea136544e4cb450.westeurope.aksapp.io"
    popd
}
