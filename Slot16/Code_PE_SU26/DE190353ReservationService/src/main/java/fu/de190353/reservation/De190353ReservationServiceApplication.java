package fu.de190353.reservation;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;

@SpringBootApplication
@EnableFeignClients // scan for @FeignClient interfaces
public class De190353ReservationServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(De190353ReservationServiceApplication.class, args);
    }
}
