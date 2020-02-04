$env:REGISTRY = "jpetereit/eshop-"
cd "$PSScriptRoot\src"
docker-compose build
docker images --format "{{.Repository}}" | grep jpetereit/eshop- | %{ docker push $_ }

cd "$PSScriptRoot\deploy\k8s\helm\"
kubectl config use-context AKS-DAK-EU-ARM-Development-202-DAKApp2
kubectl create clusterrolebinding kubernetes-dashboard -n kube-system --clusterrole=cluster-admin --serviceaccount=kube-system:kubernetes-dashboard

# .\deploy-all.ps1 -externalDns aks -aksName "AKS-DAK-EU-ARM-Development-202-DAKApp2" -aksRg "RG-202-ARM-Development" -imageTag dev -useMesh $false
.\deploy-all.ps1 -externalDns aks -aksName "AKS-DAK-EU-ARM-Development-202-DAKApp2" -aksRg "RG-202-ARM-Development" -imageTag linux-latest -useMesh $false -registry "jpetereit"

# allow large headers
kubectl apply -f aks-httpaddon-cfg.yaml
kubectl delete pod $(kubectl get pod -l app=addon-http-application-routing-nginx-ingress -n kube-system -o jsonpath="{.items[0].metadata.name}") -n kube-system


$baseUrl = kubectl get ing eshop-identity-api -o=jsonpath='{.spec.rules[0].host}'
Start-Process "http://$baseUrl/"
Start-Process "http://$baseUrl/webstatus/hc-ui#/healthchecks"
