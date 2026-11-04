package com.mss301.gateway.fallback;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.Map;

// [TODO-7.2: fallback khi CircuitBreaker OPEN]
@RestController
@RequestMapping("/fallback")
public class FallbackController {

    @RequestMapping("/account")
    public ResponseEntity<Map<String, Object>> accountFallback() {
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(Map.of(
            "success", false,
            "message", "Account Service is currently unavailable. Please try again later.",
            "timestamp", LocalDateTime.now().toString()
        ));
    }

    @RequestMapping("/brand")
    public ResponseEntity<Map<String, Object>> brandFallback() {
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(Map.of(
            "success", false,
            "message", "Brand Service is currently unavailable. Please try again later.",
            "timestamp", LocalDateTime.now().toString()
        ));
    }

    @RequestMapping("/watch")
    public ResponseEntity<Map<String, Object>> watchFallback() {
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(Map.of(
            "success", false,
            "message", "Watch Service is currently unavailable. Please try again later.",
            "timestamp", LocalDateTime.now().toString()
        ));
    }
}
