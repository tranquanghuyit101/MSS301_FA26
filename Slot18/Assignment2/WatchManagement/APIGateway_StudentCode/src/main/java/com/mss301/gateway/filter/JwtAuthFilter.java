package com.mss301.gateway.filter;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.nio.charset.StandardCharsets;
import java.util.List;

// [TODO-7.3, TODO-7.4, TODO-7.5: verify JWT, chống giả mạo header, public chỉ GET /api/watches]
@Component
public class JwtAuthFilter implements GlobalFilter, Ordered {

    private static final String USER_ID_HEADER = "X-User-Id";
    private static final String USER_ROLE_HEADER = "X-User-Role";

    @Value("${jwt.secret}")
    private String jwtSecret;

    /** Các đường dẫn KHÔNG cần JWT (mọi method). */
    private static final List<String> PUBLIC_PREFIXES = List.of(
        "/api/auth/login",
        "/api/auth/refresh",
        "/fallback"
    );

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        String path = request.getURI().getPath();

        // (1) LUÔN xoá X-User-* do client tự gửi lên -> chống giả mạo "X-User-Role: 1".
        //     Chỉ Gateway mới được phép đặt các header này sau khi verify JWT.
        ServerHttpRequest sanitized = request.mutate()
            .headers(h -> {
                h.remove(USER_ID_HEADER);
                h.remove(USER_ROLE_HEADER);
            })
            .build();

        // (2) Public: login/refresh và CHỈ "GET /api/watches" (đề bài: list không cần quyền).
        //     KHÔNG dùng startsWith("/api/watches"): như vậy POST/PUT/DELETE cũng thành public.
        boolean isPublic = PUBLIC_PREFIXES.stream().anyMatch(path::startsWith)
            || (HttpMethod.GET.equals(request.getMethod()) && path.equals("/api/watches"));
        if (isPublic) {
            return chain.filter(exchange.mutate().request(sanitized).build());
        }

        String authHeader = request.getHeaders().getFirst(HttpHeaders.AUTHORIZATION);
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }

        try {
            Claims claims = Jwts.parser()
                .verifyWith(Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8)))
                .build()
                .parseSignedClaims(authHeader.substring(7))
                .getPayload();

            if (!"access".equals(claims.get("type", String.class))) {     // refresh token không được dùng để gọi API
                exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
                return exchange.getResponse().setComplete();
            }

            // (3) Gắn thông tin user cho downstream service
            ServerHttpRequest authenticated = sanitized.mutate()
                .header(USER_ID_HEADER, claims.getSubject())
                .header(USER_ROLE_HEADER, String.valueOf(claims.get("role", Integer.class)))
                .build();
            return chain.filter(exchange.mutate().request(authenticated).build());

        } catch (Exception e) {
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }
    }

    @Override
    public int getOrder() {
        return -1; // chạy trước các filter khác
    }
}
