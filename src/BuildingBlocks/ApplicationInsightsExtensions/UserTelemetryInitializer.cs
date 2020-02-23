using Microsoft.ApplicationInsights.Channel;
using Microsoft.ApplicationInsights.Extensibility;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

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
            _logger.LogInformation($"called {nameof(UserTelemetryInitializer)}.{nameof(Initialize)}");
            var ctx = _httpContextAccessor.HttpContext;
            // If telemetry initializer is called as part of request execution and not from some async thread
            if (ctx?.User?.Identity != null)
            {
                _logger.LogInformation($"Initializing telemetry with user {ctx.User.Identity.Name}");
                telemetry.Context.User.Id = ctx.User.Identity.Name;
                telemetry.Context.Session.Id = ctx.User.Identity.Name;
            }
        }
    }
}