using Microsoft.ApplicationInsights.Extensibility;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace ApplicationInsightsExtensions
{
    public static class IServiceCollectionExtensions
    {
        public static IServiceCollection AddAppInsightsAndTelemetry(this IServiceCollection services, IConfiguration configuration)
        {
            services.AddApplicationInsightsTelemetry(configuration);
            services.AddApplicationInsightsKubernetesEnricher();
            services.AddSingleton<ITelemetryInitializer, UserTelemetryInitializer>();
            return services;
        }
    }
}
