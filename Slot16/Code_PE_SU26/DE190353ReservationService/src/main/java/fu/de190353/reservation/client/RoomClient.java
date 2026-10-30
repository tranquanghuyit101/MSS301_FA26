package fu.de190353.reservation.client;

import fu.de190353.reservation.dto.ApiResponseDTO;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

@FeignClient(name = "room-service", url = "${room.service.url}")
public interface RoomClient {

    @GetMapping("/api/rooms/{roomId}")
    ApiResponseDTO getRoomById(@PathVariable("roomId") Long roomId);
}
