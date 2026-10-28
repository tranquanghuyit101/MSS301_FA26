package fu.de190353.postservice;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;

@SpringBootApplication
@EnableFeignClients // bat quet cac @FeignClient (OpenFeign)
public class De190353PostServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(De190353PostServiceApplication.class, args);
    }
}
