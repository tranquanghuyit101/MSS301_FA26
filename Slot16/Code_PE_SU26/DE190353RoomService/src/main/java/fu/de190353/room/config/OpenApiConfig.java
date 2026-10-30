package fu.de190353.room.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI roomServiceOpenApi() {
        return new OpenAPI().info(new Info()
                .title("Room Service API")
                .version("1.0.0")
                .description("MSS301 2026 Summer PE - Room Service (Spring Boot 4.1.0)"));
    }
}
