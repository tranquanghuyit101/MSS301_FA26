package fu.de190353.room.service;

import fu.de190353.room.dto.ApiResponseDTO;
import fu.de190353.room.dto.RoomDTO;
import org.springframework.data.domain.Pageable;

public interface RoomService {
    ApiResponseDTO createRoom(RoomDTO dto);
    ApiResponseDTO updateRoom(Long roomId, RoomDTO dto);
    ApiResponseDTO getRoomById(Long roomId);
    ApiResponseDTO setRoomToMaintenance(Long roomId);
    ApiResponseDTO getRoomList(String roomType, String status, Pageable pageable);
}
