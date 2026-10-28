package fu.de190353.postservice.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * OpenFeign variant: UserClient duoc OpenFeign tu tao (xem @EnableFeignClients),
 * nen KHONG tao proxy RestClient o day nua.
 * Chi giu lai ObjectMapper de service dung convertValue(data -> UserDTO).
 */
@Configuration
public class HttpClientConfig {

    @Bean
    public ObjectMapper objectMapper() {
        return new ObjectMapper();
    }
}
