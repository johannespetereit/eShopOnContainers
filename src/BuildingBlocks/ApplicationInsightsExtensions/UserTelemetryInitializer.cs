using Microsoft.ApplicationInsights.Channel;
using Microsoft.ApplicationInsights.Extensibility;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using System;
using System.Linq;

namespace ApplicationInsightsExtensions
{
    public class UserTelemetryInitializer : ITelemetryInitializer
    {
        private readonly IHttpContextAccessor _httpContextAccessor;
        private readonly ILogger<UserTelemetryInitializer> _logger;

        public UserTelemetryInitializer(IHttpContextAccessor httpContextAccessor, ILogger<UserTelemetryInitializer> logger)
        {
            _httpContextAccessor = httpContextAccessor;
            _logger = logger;
        }
        public void Initialize(ITelemetry telemetry)
        {
            var ctx = _httpContextAccessor.HttpContext;
            if (ctx?.Request != null)
            {
                telemetry.Context.User.UserAgent = ctx.Request.Headers["User-Agent"].FirstOrDefault();
            }
            if (ctx?.User?.Identity != null)
            {
                var authHeader = ctx.Request.Headers["Authorization"].FirstOrDefault();
                telemetry.Context.User.Id = ctx.User.Identity.Name;
                telemetry.Context.Session.Id = string.IsNullOrEmpty(authHeader) ? ctx.User.Identity.Name : authHeader;
                telemetry.Context.User.AuthenticatedUserId = ctx.User.Identity.Name;
                EnrichForTest(telemetry);
            }
        }




        private void EnrichForTest(ITelemetry telemetry)
        {
            var ips = new[] { "145.195.139.91", "41.31.30.34", "181.98.130.194", "53.145.251.42", "28.235.102.232", "111.77.131.3", "102.252.220.206", "232.228.186.27", "122.28.21.110", "69.249.205.26", "164.54.216.191", "65.234.57.17", "182.251.144.26", "143.94.199.217", "83.106.232.47", "48.173.105.77", "198.156.8.207", "237.226.58.175", "94.245.101.176", "139.48.103.7", "130.136.252.102", "211.61.193.231", "175.10.162.52", "46.171.204.74", "86.160.221.252", "163.93.247.4", "113.119.36.245", "62.72.109.97", "194.60.33.169", "79.17.30.72", "177.214.48.153", "26.35.242.142", "253.176.189.59", "87.179.44.163", "188.172.109.6", "185.172.246.129", "11.201.235.118", "128.101.58.225", "122.125.53.198", "139.121.93.12", "90.30.235.117", "58.169.199.214", "12.72.165.92", "35.226.6.70", "234.206.33.232", "1.67.227.194", "86.152.207.152", "106.84.144.243", "59.237.66.172", "155.158.27.240", "98.2.138.108", "74.58.121.58", "119.111.72.147", "41.162.38.13", "171.110.53.121", "249.155.251.124", "177.110.100.101", "20.131.225.167", "237.215.71.170", "95.13.71.196", "254.10.201.205", "88.96.142.113", "32.44.143.166", "87.152.32.14", "22.30.124.16", "128.29.143.243", "205.42.57.53", "194.215.141.15", "129.77.22.241", "204.120.106.120", "205.143.153.180", "227.235.98.195", "175.192.69.133", "214.17.234.73", "129.92.76.164", "87.206.143.253", "121.233.167.186", "21.230.91.41", "165.200.216.75", "247.62.241.222", "59.40.78.23", "236.60.152.23", "132.116.245.193", "166.11.60.53", "140.171.102.249", "19.171.64.65", "229.3.197.153", "105.210.145.35", "233.183.224.242", "48.160.167.173", "180.44.63.247", "177.14.170.178", "226.214.178.28", "145.110.216.16", "195.8.33.188", "177.165.114.229", "157.185.63.181", "172.221.238.164", "175.22.162.186", "87.8.88.69", "2.20.101.195", "2.20.118.72", "2.20.97.192", "2.20.108.59", "2.20.116.71", "2.20.127.99", "2.20.126.238", "2.20.123.217", "2.20.106.47", "2.20.107.74", "2.20.126.48", "2.20.122.69", "2.20.101.217", "2.20.98.159", "2.20.107.101", "2.20.126.116", "2.20.98.9", "2.20.100.131", "2.20.125.13", "2.20.119.28" };
            telemetry.Context.Location.Ip = ips[new Random().Next(0, ips.Length - 1)];
        }
    } 
}
