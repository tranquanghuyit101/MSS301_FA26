package fu.de190353.postservice.client;

import fu.de190353.postservice.dto.ApiResponse;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

@FeignClient(name = "user-service", url = "${user.service.url}")
public interface UserClient {

    @GetMapping("/api/users/{userId}")
    ApiResponse getUserById(@PathVariable("userId") Long userId);
}
