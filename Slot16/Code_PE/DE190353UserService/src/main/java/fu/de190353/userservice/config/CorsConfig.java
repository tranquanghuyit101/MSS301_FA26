package fu.de190353.userservice.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import org.springframework.web.filter.CorsFilter;

/**
 * CORS cho service MVC (servlet). Cho phep moi origin.
 * Can thiet de Swagger UI cua MediaGateway (origin :8080) co the fetch truc tiep
 * /v3/api-docs cua service nay (cross-origin) khi gom tai lieu.
 * Dung CorsFilter (servlet filter) de ap dung cho MOI request, ke ca /v3/api-docs.
 */
@Configuration
public class CorsConfig {

    @Bean
    public CorsFilter corsFilter() {
        CorsConfiguration config = new CorsConfiguration();
        config.addAllowedOriginPattern("*");   // moi origin
        config.addAllowedMethod("*");
        config.addAllowedHeader("*");
        config.setAllowCredentials(false);     // phai false khi origin pattern la "*"

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return new CorsFilter(source);
    }
}
