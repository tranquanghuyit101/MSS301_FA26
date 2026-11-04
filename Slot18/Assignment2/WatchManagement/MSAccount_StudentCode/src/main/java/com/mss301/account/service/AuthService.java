package com.mss301.account.service;

import com.mss301.account.dto.LoginRequest;
import com.mss301.account.dto.LoginResponse;
import com.mss301.account.entity.StoreAccount;
import com.mss301.account.repository.AccountRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

// [TODO-3.3: login, refresh, kiểm tra isActive]
@Service
@RequiredArgsConstructor
public class AuthService {

    private final AccountRepository accountRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    // [TODO-3.3: login]
    public LoginResponse login(LoginRequest request) {
        StoreAccount account = accountRepository.findByUsername(request.getUsername())
            .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid username or password"));

        if (!account.getIsActive()) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Account is inactive");
        }

        if (!passwordEncoder.matches(request.getPassword(), account.getPassword())) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid username or password");
        }

        String accessToken = jwtService.generateAccessToken(account.getAccountId().toString(), account.getRole());
        String refreshToken = jwtService.generateRefreshToken(account.getAccountId().toString());

        return LoginResponse.builder()
            .accessToken(accessToken)
            .refreshToken(refreshToken)
            .tokenType("Bearer")
            .role(account.getRole())
            .username(account.getUsername())
            .build();
    }

    // [TODO-3.3: refresh token]
    public LoginResponse refresh(String refreshToken) {
        if (!jwtService.isTokenValid(refreshToken)) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid or expired refresh token");
        }
        var claims = jwtService.parseToken(refreshToken);
        String type = (String) claims.get("type");
        if (!"refresh".equals(type)) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Token is not a refresh token");
        }
        String subject = claims.getSubject();
        StoreAccount account = accountRepository.findById(Integer.parseInt(subject))
            .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Account not found"));

        String newAccessToken = jwtService.generateAccessToken(subject, account.getRole());
        String newRefreshToken = jwtService.generateRefreshToken(subject);

        return LoginResponse.builder()
            .accessToken(newAccessToken)
            .refreshToken(newRefreshToken)
            .tokenType("Bearer")
            .role(account.getRole())
            .username(account.getUsername())
            .build();
    }
}
