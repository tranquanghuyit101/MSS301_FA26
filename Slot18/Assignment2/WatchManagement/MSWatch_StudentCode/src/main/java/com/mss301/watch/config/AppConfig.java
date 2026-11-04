package com.mss301.watch.config;

import feign.Logger;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Spring Boot tự cấu hình bean tools.jackson.databind.json.JsonMapper (Jackson 3),
 * hỗ trợ sẵn LocalDate/LocalDateTime -> chỉ cần inject, không tự tạo mapper.
 */
// [TODO-6.17: Feign logger; dùng JsonMapper (Jackson 3) do Boot cấu hình]
@Configuration
public class AppConfig {

    /** BASIC: log method, URL, status, thời gian của mỗi lời gọi Feign -> thấy rõ các bước Saga gọi MSBrand. */
    @Bean
    Logger.Level feignLoggerLevel() {
        return Logger.Level.BASIC;
    }
}
