package fu.de190353.reservation.controller;

import fu.de190353.reservation.dto.ApiResponseDTO;
import fu.de190353.reservation.dto.ReservationDTO;
import fu.de190353.reservation.service.ReservationService;
import jakarta.validation.Valid;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/reservations")
public class DE190353ReservationController {

    private final ReservationService reservationService;

    public DE190353ReservationController(ReservationService reservationService) {
        this.reservationService = reservationService;
    }

    // 1. Create Reservation -> 201/1, 406/2, 404/4, 400/5, 500/0
    @PostMapping
    public ResponseEntity<ApiResponseDTO> create(@Valid @RequestBody ReservationDTO dto, BindingResult br) {
        if (br.hasErrors()) {
            return ResponseEntity.status(HttpStatus.NOT_ACCEPTABLE)
                    .body(ApiResponseDTO.error(2, firstError(br)));
        }
        return map(reservationService.createReservation(dto), HttpStatus.CREATED);
    }

    // 2. Update Reservation -> 200/1, 406/2, 404/4, 500/0
    @PutMapping("/{reservationId}")
    public ResponseEntity<ApiResponseDTO> update(@PathVariable Long reservationId,
                                                 @RequestBody ReservationDTO dto,
                                                 BindingResult br) {
        if (br.hasErrors()) {
            return ResponseEntity.status(HttpStatus.NOT_ACCEPTABLE)
                    .body(ApiResponseDTO.error(2, firstError(br)));
        }
        return map(reservationService.updateReservation(reservationId, dto), HttpStatus.OK);
    }

    // 3. Get Reservation Detail -> 200/1, 404/4, 500/0
    @GetMapping("/{reservationId}")
    public ResponseEntity<ApiResponseDTO> getById(@PathVariable Long reservationId) {
        return map(reservationService.getReservationById(reservationId), HttpStatus.OK);
    }

    // 4. Cancel Reservation -> 200/1, 404/4, 500/0
    @DeleteMapping("/{reservationId}")
    public ResponseEntity<ApiResponseDTO> cancel(@PathVariable Long reservationId) {
        return map(reservationService.cancelReservation(reservationId), HttpStatus.OK);
    }

    // 5. Get Reservation List -> 200/1, 406/2, 500/0
    @GetMapping
    public ResponseEntity<ApiResponseDTO> list(@RequestParam(defaultValue = "0") int page,
                                               @RequestParam(defaultValue = "10") int size,
                                               @RequestParam(required = false) String guestName,
                                               @RequestParam(required = false) String status) {
        if (size < 1 || size > 100) {
            return ResponseEntity.status(HttpStatus.NOT_ACCEPTABLE)
                    .body(ApiResponseDTO.error(2, "size must be between 1 and 100"));
        }
        Pageable pageable = PageRequest.of(page, size);
        return map(reservationService.getReservationList(guestName, status, pageable), HttpStatus.OK);
    }

    // -- map service status -> HTTP code --
    private ResponseEntity<ApiResponseDTO> map(ApiResponseDTO res, HttpStatus okStatus) {
        return switch (res.getStatus()) {
            case 1 -> ResponseEntity.status(okStatus).body(res);
            case 4 -> ResponseEntity.status(HttpStatus.NOT_FOUND).body(res); // 404
            case 5 -> ResponseEntity.status(HttpStatus.BAD_REQUEST).body(res); // 400 room not available
            case 0 -> ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(res);
            default -> ResponseEntity.status(HttpStatus.NOT_ACCEPTABLE).body(res); // 406 for status 2
        };
    }

    private String firstError(BindingResult br) {
        return br.getAllErrors().isEmpty() ? "Validation failed" : br.getAllErrors().get(0).getDefaultMessage();
    }
}
