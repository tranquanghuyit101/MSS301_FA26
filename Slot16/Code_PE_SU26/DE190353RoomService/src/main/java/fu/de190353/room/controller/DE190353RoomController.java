package fu.de190353.room.controller;

import fu.de190353.room.dto.ApiResponseDTO;
import fu.de190353.room.dto.RoomDTO;
import fu.de190353.room.service.RoomService;
import jakarta.validation.Valid;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/rooms")
public class DE190353RoomController {

    private final RoomService roomService;

    public DE190353RoomController(RoomService roomService) {
        this.roomService = roomService;
    }

    // 1. Create Room -> 201/1, 406/2, 226/3, 500/0
    @PostMapping
    public ResponseEntity<ApiResponseDTO> create(@Valid @RequestBody RoomDTO roomDTO, BindingResult br) {
        if (br.hasErrors()) {
            return ResponseEntity.status(HttpStatus.NOT_ACCEPTABLE) // 406
                    .body(ApiResponseDTO.error(2, firstError(br)));
        }
        return map(roomService.createRoom(roomDTO), HttpStatus.CREATED); // 201 on success
    }

    // 2. Update Room -> 200/1, 406/2, 226/3, 404/4, 500/0
    @PutMapping("/{roomId}")
    public ResponseEntity<ApiResponseDTO> update(@PathVariable Long roomId,
                                                 @RequestBody RoomDTO roomDTO,
                                                 BindingResult br) {
        if (br.hasErrors()) {
            return ResponseEntity.status(HttpStatus.NOT_ACCEPTABLE) // 406
                    .body(ApiResponseDTO.error(2, firstError(br)));
        }
        return map(roomService.updateRoom(roomId, roomDTO), HttpStatus.OK); // 200 on success
    }

    // 3. Get Room Detail -> 200/1, 404/4, 500/0
    @GetMapping("/{roomId}")
    public ResponseEntity<ApiResponseDTO> getDetail(@PathVariable Long roomId) {
        return map(roomService.getRoomById(roomId), HttpStatus.OK);
    }

    // 4. Set Room to Maintenance (delete) -> 200/1, 404/4, 500/0
    @DeleteMapping("/{roomId}")
    public ResponseEntity<ApiResponseDTO> setMaintenance(@PathVariable Long roomId) {
        return map(roomService.setRoomToMaintenance(roomId), HttpStatus.OK);
    }

    // 5. Get Room List -> 200/1, 406/2, 500/0
    @GetMapping
    public ResponseEntity<ApiResponseDTO> list(@RequestParam(required = false) String roomType,
                                               @RequestParam(required = false) String status,
                                               @RequestParam(defaultValue = "0") int page,
                                               @RequestParam(defaultValue = "10") int size) {
        if (size < 1 || size > 100) {
            return ResponseEntity.status(HttpStatus.NOT_ACCEPTABLE) // 406
                    .body(ApiResponseDTO.error(2, "size must be between 1 and 100"));
        }
        Pageable pageable = PageRequest.of(page, size);
        return map(roomService.getRoomList(roomType, status, pageable), HttpStatus.OK);
    }

    // map service status -> HTTP code
    private ResponseEntity<ApiResponseDTO> map(ApiResponseDTO apiResponse, HttpStatus okStatus) {
        int status = apiResponse.getStatus();
        HttpStatus httpStatus = switch (status) {
            case 1 -> okStatus;
            case 2 -> HttpStatus.NOT_ACCEPTABLE; // 406
            case 3 -> HttpStatus.IM_USED; // 226
            case 4 -> HttpStatus.NOT_FOUND; // 404
            default -> HttpStatus.INTERNAL_SERVER_ERROR; // 500
        };
        return ResponseEntity.status(httpStatus).body(apiResponse);
    }

    private String firstError(BindingResult br) {
        return br.getAllErrors().isEmpty() ? "Validation failed" : br.getAllErrors().get(0).getDefaultMessage();
    }
}
