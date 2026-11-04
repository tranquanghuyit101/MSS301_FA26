# Assignment 02 – SOLUTION: Watch Management Microservices (Saga Pattern)

> Lời giải cho từng TODO trong `Assignment_Readme.md`.
> Code đầy đủ nằm trong thư mục `WatchManagement/`; chỗ giải quyết mỗi TODO được đánh dấu `// [TODO-x.y]` (yml/Dockerfile: `# [TODO-x.y]`, pom: `<!-- [TODO-x.y] -->`). Tìm nhanh: `grep -rn "TODO-6.9" WatchManagement`.
> **Stack:** Java 21 · Spring Boot 4.1.1 · Spring Cloud 2025.1.3 · Hibernate 7 · Jackson 3 · SQL Server · jjwt 0.13.0

---

## Mục lục

- [Bước 0 – Git](#bước-0--git)
- [Bước 1 – Tạo project](#bước-1--tạo-project)
- [Bước 2 – Database & datasource](#bước-2--database--datasource)
- [Bước 3 – MSAccount](#bước-3--msaccount)
- [Bước 4 – Thiết kế Saga](#bước-4--thiết-kế-saga)
- [Bước 5 – MSBrand (participant)](#bước-5--msbrand-participant)
- [Bước 6 – MSWatch (orchestrator)](#bước-6--mswatch-orchestrator)
- [Bước 7 – API Gateway](#bước-7--api-gateway)
- [Bước 8 – Chạy hệ thống](#bước-8--chạy-hệ-thống)
- [Bước 9 – Kiểm thử](#bước-9--kiểm-thử)
- [Bước 10 – Docker](#bước-10--docker)
- [Lịch sử commit mẫu](#lịch-sử-commit-mẫu)
- [Lỗi thường gặp](#lỗi-thường-gặp)
- [Đáp án câu hỏi vấn đáp](#đáp-án-câu-hỏi-vấn-đáp)

---

## Bước 0 – Git

### TODO-0.1 – `.gitmessage`

```text
# [TODO-0.1] Commit message template - cài bằng: git config commit.template .gitmessage
# <type>(<scope>): <subject>          (<= 72 ký tự, tiếng Anh, động từ nguyên mẫu, không dấu chấm)
#
# type : feat | fix | refactor | build | test | docs | chore | perf | style | ci
# scope: ms-account | ms-brand | ms-watch | gateway | docker | postman | config
#
# Body (tuỳ chọn): giải thích VÌ SAO thay đổi, không chỉ LÀM GÌ. Xuống dòng ở ~72 ký tự.
#
# Footer:
#   Refs: TODO-6.9
#   BREAKING CHANGE: <mô tả thay đổi không tương thích>
#
# Cài template: git config commit.template .gitmessage
```

### TODO-0.2 – `.gitignore` và `.env.example`

```gitignore
# [TODO-0.2] Không commit file build, IDE và bí mật

# Maven / build
target/
!.mvn/wrapper/maven-wrapper.jar
*.log

# IntelliJ IDEA
.idea/
*.iml
out/

# VS Code / Eclipse
.vscode/
.classpath
.project
.settings/

# OS
.DS_Store
Thumbs.db

# Bí mật: .env chứa mật khẩu DB và JWT secret -> chỉ commit .env.example
.env
```

```properties
# [TODO-0.2] Mẫu biến môi trường. Copy thành .env rồi điền giá trị thật (KHÔNG commit .env).
JWT_SECRET=change-me-to-a-long-random-string-at-least-32-bytes
JWT_EXPIRATION=900000
REFRESH_EXPIRATION=604800000
DB_HOST=localhost
DB_PORT=1433
DB_PASSWORD=YourStrong@Password123
# true: cho phép header X-Saga-Fail-After-Step để demo compensation. Production: false
SAGA_FAULT_INJECTION=true
```

### TODO-0.3 – Commit khởi tạo

```bash
cd WatchManagement
git init -b main
git config user.name  "Nguyen Van A"
git config user.email "anv@fpt.edu.vn"
git config commit.template .gitmessage

git add .gitignore .env.example .gitmessage
git commit -m "chore: initialize repository with gitignore and env template" \
  -m "Ignore build output, IDE files and .env; provide .env.example for local setup." \
  -m "Refs: TODO-0.1, TODO-0.2, TODO-0.3"
```

---

## Bước 1 – Tạo project

### TODO-1.1 → TODO-1.5 – `pom.xml`

MSWatch (Spring Cloud + OpenFeign):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!-- [TODO-1.1, TODO-1.2, TODO-1.3, TODO-1.4, TODO-1.5: Boot 4.1.1, Spring Cloud 2025.1.3 + OpenFeign, springdoc, Lombok] -->
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>4.1.1</version>
        <relativePath/>
    </parent>
    <groupId>com.mss301</groupId>
    <artifactId>ms-watch</artifactId>
    <version>1.0.0</version>
    <description>Watch service - Saga orchestrator</description>
    <properties>
        <java.version>21</java.version>
        <spring-cloud.version>2025.1.3</spring-cloud.version>
        <springdoc.version>3.0.2</springdoc.version>
    </properties>
    <dependencies>
        <!-- Spring MVC + Tomcat: REST API -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-webmvc</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>com.microsoft.sqlserver</groupId>
            <artifactId>mssql-jdbc</artifactId>
            <scope>runtime</scope>
        </dependency>
        <!-- OpenFeign: gọi MSBrand (participant của Saga) -->
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter-openfeign</artifactId>
        </dependency>
        <!-- Swagger UI / OpenAPI (springdoc 3.x cho Spring Boot 4) -->
        <dependency>
            <groupId>org.springdoc</groupId>
            <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
            <version>${springdoc.version}</version>
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
    </dependencies>

    <!-- Spring Cloud 2025.1.x (Oakwood): release train dành cho Spring Boot 4.0.x / 4.1.x -->
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.cloud</groupId>
                <artifactId>spring-cloud-dependencies</artifactId>
                <version>${spring-cloud.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <configuration>
                    <annotationProcessorPaths>
                        <path>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </path>
                    </annotationProcessorPaths>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

API Gateway (Gateway server WebFlux + Resilience4j + jjwt):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!-- [TODO-1.1, TODO-1.3, TODO-1.4, TODO-1.5: Boot 4.1.1, Spring Cloud 2025.1.3, gateway-server-webflux, circuitbreaker, jjwt] -->
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>4.1.1</version>
        <relativePath/>
    </parent>
    <groupId>com.mss301</groupId>
    <artifactId>api-gateway</artifactId>
    <version>1.0.0</version>
    <description>API Gateway - JWT + routing</description>
    <properties>
        <java.version>21</java.version>
        <spring-cloud.version>2025.1.3</spring-cloud.version>
        <jjwt.version>0.13.0</jjwt.version>
    </properties>
    <dependencies>
        <!-- Spring Cloud Gateway (server WebFlux, reactive) -->
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter-gateway-server-webflux</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter-circuitbreaker-reactor-resilience4j</artifactId>
        </dependency>
        <dependency>
            <groupId>io.jsonwebtoken</groupId>
            <artifactId>jjwt-api</artifactId>
            <version>${jjwt.version}</version>
        </dependency>
        <dependency>
            <groupId>io.jsonwebtoken</groupId>
            <artifactId>jjwt-impl</artifactId>
            <version>${jjwt.version}</version>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>io.jsonwebtoken</groupId>
            <artifactId>jjwt-jackson</artifactId>
            <version>${jjwt.version}</version>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
    </dependencies>

    <!-- Spring Cloud 2025.1.x (Oakwood): release train dành cho Spring Boot 4.0.x / 4.1.x -->
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.cloud</groupId>
                <artifactId>spring-cloud-dependencies</artifactId>
                <version>${spring-cloud.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <configuration>
                    <annotationProcessorPaths>
                        <path>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </path>
                    </annotationProcessorPaths>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

MSAccount (Security + jjwt). MSBrand giống MSAccount nhưng không có `security` và `jjwt`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!-- [TODO-1.1, TODO-1.2, TODO-1.4, TODO-1.5: Boot 4.1.1, webmvc + data-jpa + security + validation, jjwt, springdoc, Lombok] -->
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>4.1.1</version>
        <relativePath/>
    </parent>
    <groupId>com.mss301</groupId>
    <artifactId>ms-account</artifactId>
    <version>1.0.0</version>
    <description>Account service - login + JWT</description>
    <properties>
        <java.version>21</java.version>
        <jjwt.version>0.13.0</jjwt.version>
        <springdoc.version>3.0.2</springdoc.version>
    </properties>
    <dependencies>
        <!-- Spring MVC + Tomcat: REST API -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-webmvc</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-security</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>com.microsoft.sqlserver</groupId>
            <artifactId>mssql-jdbc</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>io.jsonwebtoken</groupId>
            <artifactId>jjwt-api</artifactId>
            <version>${jjwt.version}</version>
        </dependency>
        <dependency>
            <groupId>io.jsonwebtoken</groupId>
            <artifactId>jjwt-impl</artifactId>
            <version>${jjwt.version}</version>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>io.jsonwebtoken</groupId>
            <artifactId>jjwt-jackson</artifactId>
            <version>${jjwt.version}</version>
            <scope>runtime</scope>
        </dependency>
        <!-- Swagger UI / OpenAPI (springdoc 3.x cho Spring Boot 4) -->
        <dependency>
            <groupId>org.springdoc</groupId>
            <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
            <version>${springdoc.version}</version>
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <configuration>
                    <annotationProcessorPaths>
                        <path>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </path>
                    </annotationProcessorPaths>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

**Điểm cần kiểm tra khi chấm:** parent `4.1.1`; `spring-boot-starter-webmvc` (3 service MVC); BOM `spring-cloud-dependencies 2025.1.3` (MSWatch, Gateway); springdoc `3.0.2`; jjwt `0.13.0`; Lombok trong `annotationProcessorPaths`.

### 📝 Commit – Bước 1

> Nhánh `feature/scaffold` tiếp tục dùng cho Bước 2, merge ở cuối Bước 2.

```bash
git switch -c feature/scaffold

git add MSAccount_StudentCode/pom.xml \
        MSBrand_StudentCode/pom.xml \
        MSAccount_StudentCode/src/main/java/com/mss301/account/MSAccountApplication.java \
        MSBrand_StudentCode/src/main/java/com/mss301/brand/MSBrandApplication.java
git commit -m "build: scaffold account and brand services on Spring Boot 4.1.1" \
  -m "Spring MVC, Data JPA, validation, SQL Server driver, springdoc 3 and Lombok annotation processing; jjwt 0.13 and security for account." \
  -m "Refs: TODO-1.1, TODO-1.2, TODO-1.4, TODO-1.5"

git add MSWatch_StudentCode/pom.xml \
        APIGateway_StudentCode/pom.xml \
        MSWatch_StudentCode/src/main/java/com/mss301/watch/MSWatchApplication.java \
        APIGateway_StudentCode/src/main/java/com/mss301/gateway/GatewayApplication.java
git commit -m "build: scaffold watch service and gateway with Spring Cloud 2025.1.3" \
  -m "OpenFeign for the watch service; Gateway server WebFlux with Resilience4j circuit breaker and jjwt for the gateway." \
  -m "Refs: TODO-1.1, TODO-1.3, TODO-1.4, TODO-1.5"
```

---

## Bước 2 – Database & datasource

### TODO-2.1 – Tạo database

```sql
CREATE DATABASE DBAccount;
CREATE DATABASE DBBrand;
CREATE DATABASE DBWatch;
GO
ALTER LOGIN sa ENABLE;
ALTER LOGIN sa WITH PASSWORD = 'YourStrong@Password123';
```

### TODO-2.2 – Datasource (ví dụ MSBrand)

```yaml
# [TODO-2.2: datasource DBBrand + naming strategy]
server:
  port: 8082

spring:
  application:
    name: ms-brand
  datasource:
    url: jdbc:sqlserver://${DB_HOST:localhost}:${DB_PORT:1433};databaseName=DBBrand;encrypt=true;trustServerCertificate=true
    username: sa
    password: ${DB_PASSWORD:YourStrong@Password123}
    driver-class-name: com.microsoft.sqlserver.jdbc.SQLServerDriver
  jpa:
    open-in-view: false
    hibernate:
      ddl-auto: update
      naming:
        # Giữ NGUYÊN tên trong @Table/@Column (StoreAccounts, WatchID...) đúng như đề bài.
        # Mặc định Spring Boot đổi thành store_accounts, watch_id...
        physical-strategy: org.hibernate.boot.model.naming.PhysicalNamingStrategyStandardImpl
    show-sql: false

logging:
  level:
    com.mss301.brand: INFO
```

> `PhysicalNamingStrategyStandardImpl` giữ nguyên tên `@Table`/`@Column` (`StoreAccounts`, `WatchID`); mặc định Spring Boot đổi thành `store_accounts`, `watch_id`.

### 📝 Commit – Bước 2

> Ở bước này `MSWatch_StudentCode/application.yml` mới chỉ có phần datasource; phần Feign và `saga.*` được thêm và commit ở Bước 6 (TODO-6.1).

```bash
git switch -c feature/scaffold

git add MSAccount_StudentCode/src/main/resources/application.yml \
        MSBrand_StudentCode/src/main/resources/application.yml \
        MSWatch_StudentCode/src/main/resources/application.yml
git commit -m "chore(config): configure SQL Server datasources and naming strategy" \
  -m "One database per service; keep table and column names exactly as declared in the entities." \
  -m "Refs: TODO-2.1, TODO-2.2"

# Build pass + checklist xong mới merge
git switch main
git merge --no-ff feature/scaffold -m "Merge branch 'feature/scaffold'"
```

---

## Bước 3 – MSAccount

### TODO-3.1 – Entity, repository, seed

```java
package com.mss301.account.entity;

import jakarta.persistence.*;
import lombok.*;

// [TODO-3.1: entity StoreAccounts (@Builder.Default cho isActive)]
@Entity
@Table(name = "StoreAccounts")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class StoreAccount {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "AccountID")
    private Integer accountId;

    @Column(name = "Username", nullable = false, length = 20)
    private String username;

    @Column(name = "Email", nullable = false, length = 100)
    private String email;

    @Column(name = "Password", nullable = false, length = 100)
    private String password;

    @Column(name = "Role")
    private Integer role; // 1=Admin, 2=Staff, 3=Member

    @Column(name = "IsActive", columnDefinition = "BIT DEFAULT 1")
    @Builder.Default            // nếu thiếu, builder sẽ bỏ qua giá trị mặc định = true
    private Boolean isActive = true;
}
```

```java
package com.mss301.account;

import com.mss301.account.entity.StoreAccount;
import com.mss301.account.repository.AccountRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import java.util.List;

// [TODO-3.1: seed 5 tài khoản, mật khẩu BCrypt]
@Component
@RequiredArgsConstructor
@Slf4j
public class DataInitializer implements CommandLineRunner {

    private final AccountRepository accountRepository;
    private final PasswordEncoder passwordEncoder;

    @Override
    public void run(String... args) {
        if (accountRepository.count() == 0) {
            String encoded = passwordEncoder.encode("@1");
            List<StoreAccount> accounts = List.of(
                StoreAccount.builder().username("adminsys").email("admin@drawingpen.com.vn").password(encoded).role(1).isActive(true).build(),
                StoreAccount.builder().username("staff02").email("staff02@drawingpen.com.vn").password(encoded).role(2).isActive(true).build(),
                StoreAccount.builder().username("member01").email("member01@drawingpen.com.vn").password(encoded).role(3).isActive(true).build(),
                StoreAccount.builder().username("member02").email("member02@drawingpen.com.vn").password(encoded).role(3).isActive(false).build(),
                StoreAccount.builder().username("staff01").email("staff01@drawingpen.com.vn").password(encoded).role(2).isActive(false).build()
            );
            accountRepository.saveAll(accounts);
            log.info("Seeded {} accounts", accounts.size());
        }
    }
}
```

### TODO-3.2 – `JwtService` + cấu hình JWT

```java
package com.mss301.account.service;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

// [TODO-3.2: phát / kiểm tra access token & refresh token]
@Service
public class JwtService {

    @Value("${jwt.secret}")
    private String secret;

    @Value("${jwt.expiration}")
    private long expiration;

    @Value("${jwt.refresh-expiration}")
    private long refreshExpiration;

    public String generateAccessToken(String subject, Integer role) {
        Map<String, Object> claims = new HashMap<>();
        claims.put("role", role);
        claims.put("type", "access");
        return Jwts.builder()
            .subject(subject)
            .claims(claims)
            .issuedAt(new Date())
            .expiration(new Date(System.currentTimeMillis() + expiration))
            .signWith(Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8)))
            .compact();
    }

    public String generateRefreshToken(String subject) {
        Map<String, Object> claims = new HashMap<>();
        claims.put("type", "refresh");
        return Jwts.builder()
            .subject(subject)
            .claims(claims)
            .issuedAt(new Date())
            .expiration(new Date(System.currentTimeMillis() + refreshExpiration))
            .signWith(Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8)))
            .compact();
    }

    public Claims parseToken(String token) {
        return Jwts.parser()
            .verifyWith(Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8)))
            .build()
            .parseSignedClaims(token)
            .getPayload();
    }

    public boolean isTokenValid(String token) {
        try {
            parseToken(token);
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}
```

```yaml
# [TODO-2.2, TODO-3.2: datasource DBAccount + naming strategy, cấu hình JWT]
server:
  port: 8081

spring:
  application:
    name: ms-account
  datasource:
    url: jdbc:sqlserver://${DB_HOST:localhost}:${DB_PORT:1433};databaseName=DBAccount;encrypt=true;trustServerCertificate=true
    username: sa
    password: ${DB_PASSWORD:YourStrong@Password123}
    driver-class-name: com.microsoft.sqlserver.jdbc.SQLServerDriver
  jpa:
    open-in-view: false
    hibernate:
      ddl-auto: update
      naming:
        # Giữ NGUYÊN tên trong @Table/@Column (StoreAccounts, WatchID...) đúng như đề bài.
        # Mặc định Spring Boot đổi thành store_accounts, watch_id...
        physical-strategy: org.hibernate.boot.model.naming.PhysicalNamingStrategyStandardImpl
    show-sql: true
    # Hibernate 7 tự nhận dialect SQL Server từ JDBC metadata -> không cần khai báo hibernate.dialect

jwt:
  secret: ${JWT_SECRET:mss301-watch-management-secret-key-2025-very-long-string}
  expiration: ${JWT_EXPIRATION:900000}
  refresh-expiration: ${REFRESH_EXPIRATION:604800000}
```

### TODO-3.3 – `AuthService`

```java
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
```

### TODO-3.4 – `AuthController`, `SecurityConfig`

```java
package com.mss301.account.controller;

import com.mss301.account.dto.ApiResponse;
import com.mss301.account.dto.LoginRequest;
import com.mss301.account.dto.LoginResponse;
import com.mss301.account.service.AuthService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

// [TODO-3.4: /api/auth/login, /refresh, /logout]
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
@Tag(name = "Authentication", description = "Login, Refresh Token, Logout")
public class AuthController {

    private final AuthService authService;

    @PostMapping("/login")
    @Operation(summary = "Login and get JWT tokens")
    public ResponseEntity<ApiResponse<LoginResponse>> login(@Valid @RequestBody LoginRequest request) {
        LoginResponse response = authService.login(request);
        return ResponseEntity.ok(ApiResponse.success(response, "Login successful"));
    }

    @PostMapping("/refresh")
    @Operation(summary = "Get new access token using refresh token")
    public ResponseEntity<ApiResponse<LoginResponse>> refresh(@RequestBody Map<String, String> body) {
        String refreshToken = body.get("refreshToken");
        LoginResponse response = authService.refresh(refreshToken);
        return ResponseEntity.ok(ApiResponse.success(response, "Token refreshed"));
    }

    @PostMapping("/logout")
    @Operation(summary = "Logout (client should discard tokens)")
    public ResponseEntity<ApiResponse<Void>> logout() {
        return ResponseEntity.ok(ApiResponse.success(null, "Logged out successfully"));
    }
}
```

```java
package com.mss301.account.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

// [TODO-3.4: permitAll + BCryptPasswordEncoder (JWT verify ở Gateway)]
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http.csrf(AbstractHttpConfigurer::disable)
            .authorizeHttpRequests(auth -> auth.anyRequest().permitAll());
        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

### TODO-3.5 – Kết quả test mong đợi

```http
POST http://localhost:8081/api/auth/login
Content-Type: application/json

{ "username": "adminsys", "password": "@1" }
```

```json
{
  "success": true,
  "message": "Login successful",
  "data": { "accessToken": "eyJ...", "refreshToken": "eyJ...", "tokenType": "Bearer", "role": 1, "username": "adminsys" }
}
```

### 📝 Commit – Bước 3

> `JwtService` chưa có ai gọi ở commit 2 nhưng vẫn build được; `AuthService` dùng nó ở commit 3.

```bash
git switch -c feature/ms-account

git add MSAccount_StudentCode/src/main/java/com/mss301/account/entity \
        MSAccount_StudentCode/src/main/java/com/mss301/account/repository \
        MSAccount_StudentCode/src/main/java/com/mss301/account/DataInitializer.java
git commit -m "feat(ms-account): add store account entity and seed data" \
  -m "Passwords are stored as BCrypt hashes." \
  -m "Refs: TODO-3.1"

git add MSAccount_StudentCode/src/main/java/com/mss301/account/service/JwtService.java \
        MSAccount_StudentCode/src/main/resources/application.yml
git commit -m "feat(ms-account): issue access and refresh tokens with jjwt" \
  -m "Refs: TODO-3.2"

git add MSAccount_StudentCode/src/main/java/com/mss301/account/service/AuthService.java \
        MSAccount_StudentCode/src/main/java/com/mss301/account/controller \
        MSAccount_StudentCode/src/main/java/com/mss301/account/config \
        MSAccount_StudentCode/src/main/java/com/mss301/account/dto \
        MSAccount_StudentCode/src/main/java/com/mss301/account/exception
git commit -m "feat(ms-account): implement login and refresh endpoints" \
  -m "Inactive accounts are rejected with 403 before the password check." \
  -m "Refs: TODO-3.3, TODO-3.4"

# Build pass + checklist xong mới merge
git switch main
git merge --no-ff feature/ms-account -m "Merge branch 'feature/ms-account'"
```

---

## Bước 4 – Thiết kế Saga

### TODO-4.1 – `docs/SAGA_DESIGN.md`

````markdown
# Saga Design – Watch Management

> [TODO-4.1] Tài liệu thiết kế Saga (sinh viên tự điền trước khi code).

## Participants

| Service | Vai trò | Database | Dữ liệu tham gia Saga |
|---|---|---|---|
| MSWatch | Orchestrator | DBWatch | `Watches`, `SagaStates`, `SagaLogs` |
| MSBrand | Participant | DBBrand | `BrandWatches` |

## Saga CREATE_WATCH

| # | Local transaction | Service / DB | Compensation | Idempotent? |
|---|---|---|---|---|
| 1 | CREATE_WATCH – INSERT Watches | MSWatch / DBWatch | DELETE_WATCH | ✔ (`deleteIfExists`) |
| 2 | ASSIGN_BRAND – upsert BrandWatches | MSBrand / DBBrand | UNASSIGN_BRAND | ✔ |

## Saga UPDATE_WATCH

| # | Local transaction | Service / DB | Compensation | Idempotent? |
|---|---|---|---|---|
| 1 | UPDATE_WATCH | MSWatch / DBWatch | RESTORE_WATCH (snapshot `before`) | ✔ |
| 2 | ASSIGN_BRAND (brand mới) | MSBrand / DBBrand | ASSIGN_BRAND_BACK (brand cũ) | ✔ |

## Saga DELETE_WATCH

| # | Local transaction | Service / DB | Compensation | Idempotent? |
|---|---|---|---|---|
| 1 | UNASSIGN_BRAND | MSBrand / DBBrand | ASSIGN_BRAND_BACK | ✔ |
| 2 | DELETE_WATCH | MSWatch / DBWatch | — **PIVOT** | — |

## State machine

```
PENDING → EXECUTING → COMPLETED
               └→ FAILED → COMPENSATING → COMPENSATED
                                 └→ (compensation lỗi) dừng ở COMPENSATING
```

## Quyết định thiết kế

1. Orchestration (không dùng Choreography) vì chỉ có 2 service, luồng ngắn, dễ quan sát.
2. Orchestrator không có `@Transactional`; mỗi bước là 1 local transaction.
3. Compensation chạy LIFO, retry tối đa 3 lần, yêu cầu idempotent.
4. Bước xoá cứng (`DELETE_WATCH`) là pivot, đặt cuối Saga xoá.
5. Validate rẻ (name, price, releaseDate, category) chạy trước khi Saga bắt đầu.
````

### TODO-4.2 – Vì sao không dùng `@Transactional` / 2PC

- `@Transactional` chỉ quản lý **một** database (DBWatch). Lời gọi HTTP sang MSBrand nằm ngoài transaction, nên rollback DBWatch không hoàn tác được DBBrand.
- 2PC phải lock tài nguyên ở cả hai service trong suốt 2 pha; coordinator là single point of failure; MSBrand không hỗ trợ XA qua REST.
- Saga chấp nhận **eventual consistency**: mỗi bước commit ngay, lỗi thì bù trừ.

### 📝 Commit – Bước 4

```bash
git switch -c docs/saga-design

git add docs/SAGA_DESIGN.md
git commit -m "docs: add saga design for watch create, update and delete" \
  -m "Define local transactions, compensations, pivot step and state machine before implementation." \
  -m "Refs: TODO-4.1"

# Build pass + checklist xong mới merge
git switch main
git merge --no-ff docs/saga-design -m "Merge branch 'docs/saga-design'"
```

---

## Bước 5 – MSBrand (participant)

### TODO-5.1 – Entity & repository

```java
package com.mss301.brand.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

/**
 * Dữ liệu mà MSBrand sở hữu về quan hệ Brand - Watch.
 * <p>
 * Đây là phần "update other related Microservices" của đề bài: mỗi khi MSWatch
 * thêm / sửa / xoá đồng hồ, MSBrand phải cập nhật bảng này trong DB của chính nó (DBBrand).
 * Hai bảng Watches (DBWatch) và BrandWatches (DBBrand) nằm ở 2 database khác nhau,
 * nên KHÔNG thể dùng 1 transaction ACID -> phải dùng Saga để giữ chúng nhất quán.
 */
@Entity
@Table(name = "BrandWatches",
       uniqueConstraints = @UniqueConstraint(name = "UQ_BrandWatches_WatchID", columnNames = "WatchID"))
// [TODO-5.1: bảng BrandWatches (dữ liệu MSBrand sở hữu)]
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class BrandWatch {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "Id")
    private Long id;

    @Column(name = "WatchID", nullable = false)
    private Integer watchId;          // 1 watch chỉ thuộc 1 brand -> unique

    @Column(name = "BrandID", nullable = false)
    private Integer brandId;

    @Column(name = "UpdatedAt")
    private LocalDateTime updatedAt;
}
```

```java
package com.mss301.brand.repository;

import com.mss301.brand.entity.BrandWatch;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

// [TODO-5.1]
public interface BrandWatchRepository extends JpaRepository<BrandWatch, Long> {

    Optional<BrandWatch> findByWatchId(Integer watchId);

    long countByBrandId(Integer brandId);

    List<BrandWatch> findByBrandIdOrderByWatchIdAsc(Integer brandId);
}
```

### TODO-5.2, TODO-5.3, TODO-5.5 – `BrandService`

```java
package com.mss301.brand.service;

import com.mss301.brand.dto.AssignmentResponse;
import com.mss301.brand.dto.BrandResponse;
import com.mss301.brand.dto.BrandWatchesResponse;
import com.mss301.brand.entity.BrandWatch;
import com.mss301.brand.entity.WatchBrand;
import com.mss301.brand.repository.BrandRepository;
import com.mss301.brand.repository.BrandWatchRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.time.LocalDateTime;
import java.util.List;

// [TODO-5.2, TODO-5.3, TODO-5.5: local transaction + compensation idempotent, truy vấn brand]
@Service
@RequiredArgsConstructor
@Slf4j
public class BrandService {

    private final BrandRepository brandRepository;
    private final BrandWatchRepository brandWatchRepository;

    // ===================== Public API (đọc) =====================

    public List<BrandResponse> findAll() {
        return brandRepository.findAll().stream().map(this::toResponse).toList();
    }

    public BrandResponse findById(Integer id) {
        return toResponse(getBrand(id));
    }

    public boolean existsById(Integer id) {
        return brandRepository.existsById(id);
    }

    // [TODO-5.5]
    public BrandWatchesResponse watchesOf(Integer brandId) {
        WatchBrand brand = getBrand(brandId);
        List<Integer> ids = brandWatchRepository.findByBrandIdOrderByWatchIdAsc(brandId).stream()
            .map(BrandWatch::getWatchId).toList();
        return new BrandWatchesResponse(brandId, brand.getBrandName(), ids.size(), ids);
    }

    // ============ Internal API cho Saga (LOCAL TRANSACTION trên DBBrand) ============

    /**
     * Gán watch vào brand (upsert).
     * - Brand không tồn tại -> 404 => MSWatch hiểu là bước Saga thất bại và sẽ compensate.
     * - IDEMPOTENT: gọi lại nhiều lần với cùng (brandId, watchId) cho cùng một kết quả.
     * - Dùng cho cả: CREATE (gán mới), UPDATE (chuyển brand), và compensation của DELETE/UPDATE (gán lại brand cũ).
     */
    // [TODO-5.2: gán watch (upsert, idempotent)]
    @Transactional
    public AssignmentResponse assignWatch(Integer brandId, Integer watchId) {
        if (!brandRepository.existsById(brandId)) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Brand not found with id: " + brandId);
        }
        BrandWatch link = brandWatchRepository.findByWatchId(watchId)
            .orElseGet(() -> BrandWatch.builder().watchId(watchId).build());
        Integer previous = link.getBrandId();

        link.setBrandId(brandId);
        link.setUpdatedAt(LocalDateTime.now());
        brandWatchRepository.save(link);

        log.info("[SAGA-PARTICIPANT] ASSIGN watch={} -> brand={} (previous brand={})", watchId, brandId, previous);
        return new AssignmentResponse(watchId, brandId, previous, "ASSIGNED");
    }

    /**
     * Gỡ watch khỏi brand.
     * - IDEMPOTENT: watch chưa từng gán / đã gỡ rồi -> vẫn trả 200, không lỗi.
     * - Dùng cho: DELETE (bước 1) và compensation của CREATE.
     */
    // [TODO-5.3: gỡ watch (idempotent)]
    @Transactional
    public AssignmentResponse unassignWatch(Integer watchId) {
        var existing = brandWatchRepository.findByWatchId(watchId);
        if (existing.isEmpty()) {
            log.info("[SAGA-PARTICIPANT] UNASSIGN watch={} -> nothing to do (idempotent)", watchId);
            return new AssignmentResponse(watchId, null, null, "NOTHING_TO_DO");
        }
        Integer previous = existing.get().getBrandId();
        brandWatchRepository.delete(existing.get());
        log.info("[SAGA-PARTICIPANT] UNASSIGN watch={} from brand={}", watchId, previous);
        return new AssignmentResponse(watchId, null, previous, "UNASSIGNED");
    }

    // ===================== helpers =====================

    private WatchBrand getBrand(Integer id) {
        return brandRepository.findById(id)
            .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Brand not found with id: " + id));
    }

    private BrandResponse toResponse(WatchBrand b) {
        return BrandResponse.builder()
            .brandId(b.getBrandId())
            .brandName(b.getBrandName())
            .countryOfOrigin(b.getCountryOfOrigin())
            .watchCount(brandWatchRepository.countByBrandId(b.getBrandId()))
            .build();
    }
}
```

- `assignWatch` là upsert theo `WatchID` → gọi lặp lại cho cùng kết quả; dùng cho cả bước Saga lẫn compensation (gán lại brand cũ).
- `unassignWatch` trả `NOTHING_TO_DO` thay vì lỗi khi không có gì để gỡ.

### TODO-5.4 – API nội bộ + xử lý lỗi

```java
package com.mss301.brand.controller;

import com.mss301.brand.dto.ApiResponse;
import com.mss301.brand.dto.AssignmentResponse;
import com.mss301.brand.service.BrandService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * API NỘI BỘ - chỉ MSWatch (Saga Orchestrator) gọi trực tiếp tới cổng 8082.
 * API Gateway KHÔNG định tuyến /internal/** nên client bên ngoài không gọi được.
 * <p>
 * Mỗi endpoint = 1 local transaction của Saga (hoặc 1 compensating transaction), và đều IDEMPOTENT.
 */
// [TODO-5.4: API nội bộ /internal/brands/** cho Saga]
@RestController
@RequestMapping("/internal/brands")
@RequiredArgsConstructor
@Tag(name = "Internal (Saga)", description = "Called only by MSWatch saga orchestrator")
public class InternalBrandController {

    private final BrandService brandService;

    @PutMapping("/{brandId}/watches/{watchId}")
    @Operation(summary = "Gán watch vào brand (upsert, idempotent)")
    public ResponseEntity<ApiResponse<AssignmentResponse>> assign(@PathVariable Integer brandId,
                                                                  @PathVariable Integer watchId) {
        return ResponseEntity.ok(ApiResponse.success(brandService.assignWatch(brandId, watchId), "Assigned"));
    }

    @DeleteMapping("/watches/{watchId}")
    @Operation(summary = "Gỡ watch khỏi brand (idempotent)")
    public ResponseEntity<ApiResponse<AssignmentResponse>> unassign(@PathVariable Integer watchId) {
        return ResponseEntity.ok(ApiResponse.success(brandService.unassignWatch(watchId), "Unassigned"));
    }
}
```

```java
package com.mss301.brand.exception;

import com.mss301.brand.dto.ApiResponse;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.server.ResponseStatusException;

// [TODO-5.4: trả lỗi dạng ApiResponse]
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ResponseStatusException.class)
    public ResponseEntity<ApiResponse<Void>> handleResponseStatus(ResponseStatusException ex) {
        return ResponseEntity.status(ex.getStatusCode())
            .body(ApiResponse.error(ex.getReason()));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleGeneral(Exception ex) {
        return ResponseEntity.internalServerError()
            .body(ApiResponse.error("Internal error: " + ex.getMessage()));
    }
}
```

### TODO-5.5 – API public

```java
package com.mss301.brand.controller;

import com.mss301.brand.dto.ApiResponse;
import com.mss301.brand.dto.BrandResponse;
import com.mss301.brand.dto.BrandWatchesResponse;
import com.mss301.brand.service.BrandService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/** API public - đi qua API Gateway (cần JWT). */
// [TODO-5.5: API public /api/brands, /{id}, /{id}/watches]
@RestController
@RequestMapping("/api/brands")
@RequiredArgsConstructor
@Tag(name = "Brand", description = "Watch Brand management")
public class BrandController {

    private final BrandService brandService;

    @GetMapping
    @Operation(summary = "Get all brands (kèm watchCount)")
    public ResponseEntity<ApiResponse<List<BrandResponse>>> findAll() {
        return ResponseEntity.ok(ApiResponse.success(brandService.findAll(), "Success"));
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get brand by ID")
    public ResponseEntity<ApiResponse<BrandResponse>> findById(@PathVariable Integer id) {
        return ResponseEntity.ok(ApiResponse.success(brandService.findById(id), "Success"));
    }

    @GetMapping("/{id}/watches")
    @Operation(summary = "Danh sách watchId đang gắn với brand (dùng để kiểm chứng Saga)")
    public ResponseEntity<ApiResponse<BrandWatchesResponse>> watches(@PathVariable Integer id) {
        return ResponseEntity.ok(ApiResponse.success(brandService.watchesOf(id), "Success"));
    }

    @GetMapping("/{id}/exists")
    @Operation(summary = "Check if brand exists")
    public ResponseEntity<Boolean> exists(@PathVariable Integer id) {
        return ResponseEntity.ok(brandService.existsById(id));
    }
}
```

### TODO-5.6 – Seed

```java
package com.mss301.brand;

import com.mss301.brand.entity.BrandWatch;
import com.mss301.brand.entity.WatchBrand;
import com.mss301.brand.repository.BrandRepository;
import com.mss301.brand.repository.BrandWatchRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

// [TODO-5.6: seed 5 brand + BrandWatches khớp 10 watch của đề bài]
@Component
@RequiredArgsConstructor
@Slf4j
public class DataInitializer implements CommandLineRunner {

    private final BrandRepository brandRepository;
    private final BrandWatchRepository brandWatchRepository;

    @Override
    public void run(String... args) {
        if (brandRepository.count() == 0) {
            List<WatchBrand> brands = List.of(
                WatchBrand.builder().brandName("Rolex").countryOfOrigin("Switzerland").build(),
                WatchBrand.builder().brandName("Omega").countryOfOrigin("Switzerland").build(),
                WatchBrand.builder().brandName("Seiko").countryOfOrigin("Japan").build(),
                WatchBrand.builder().brandName("Casio").countryOfOrigin("Japan").build(),
                WatchBrand.builder().brandName("TAG Heuer").countryOfOrigin("Switzerland").build()
            );
            brandRepository.saveAll(brands);
            log.info("Seeded {} brands", brands.size());
        }

        // Trạng thái ban đầu phải KHỚP với 10 watch seed trong DBWatch (WatchID -> BrandID theo đề bài).
        // Lưu ý: chỉ đúng khi DBWatch và DBBrand cùng được tạo mới (WatchID chạy từ 1..10).
        if (brandWatchRepository.count() == 0) {
            Map<Integer, Integer> watchToBrand = new LinkedHashMap<>();
            watchToBrand.put(1, 1);  watchToBrand.put(2, 2);  watchToBrand.put(3, 3);
            watchToBrand.put(4, 4);  watchToBrand.put(5, 5);  watchToBrand.put(6, 2);
            watchToBrand.put(7, 3);  watchToBrand.put(8, 1);  watchToBrand.put(9, 4);
            watchToBrand.put(10, 4);
            watchToBrand.forEach((watchId, brandId) -> brandWatchRepository.save(
                BrandWatch.builder().watchId(watchId).brandId(brandId).updatedAt(LocalDateTime.now()).build()));
            log.info("Seeded {} brand-watch links", watchToBrand.size());
        }
    }
}
```

### 📝 Commit – Bước 5

> Mỗi commit phải **build được** (`mvn -q -DskipTests compile` trong service tương ứng). Thứ tự commit bên dưới đã được sắp để thoả điều này.

```bash
git switch -c feature/ms-brand-participant

git add MSBrand_StudentCode/src/main/java/com/mss301/brand/entity \
        MSBrand_StudentCode/src/main/java/com/mss301/brand/repository \
        MSBrand_StudentCode/src/main/java/com/mss301/brand/DataInitializer.java
git commit -m "feat(ms-brand): add brand and brand-watch entities with seed data" \
  -m "BrandWatches is owned by the brand service, so every watch change must update a second database." \
  -m "Refs: TODO-5.1, TODO-5.6"

git add MSBrand_StudentCode/src/main/java/com/mss301/brand/service \
        MSBrand_StudentCode/src/main/java/com/mss301/brand/controller/InternalBrandController.java \
        MSBrand_StudentCode/src/main/java/com/mss301/brand/dto \
        MSBrand_StudentCode/src/main/java/com/mss301/brand/exception
git commit -m "feat(ms-brand): expose idempotent internal assign and unassign API" \
  -m "These endpoints are saga steps and compensations; they must be safe to retry." \
  -m "Refs: TODO-5.2, TODO-5.3, TODO-5.4"

git add MSBrand_StudentCode/src/main/java/com/mss301/brand/controller/BrandController.java
git commit -m "feat(ms-brand): add public brand endpoints with watch count" \
  -m "Refs: TODO-5.5"

# Build pass + checklist xong mới merge
git switch main
git merge --no-ff feature/ms-brand-participant -m "Merge branch 'feature/ms-brand-participant'"
```

---

## Bước 6 – MSWatch (orchestrator)

### TODO-6.1 – `application.yml`

```yaml
# [TODO-2.2, TODO-6.1: datasource DBWatch + naming strategy, Feign timeout, cấu hình saga]
server:
  port: 8083

spring:
  application:
    name: ms-watch
  datasource:
    url: jdbc:sqlserver://${DB_HOST:localhost}:${DB_PORT:1433};databaseName=DBWatch;encrypt=true;trustServerCertificate=true
    username: sa
    password: ${DB_PASSWORD:YourStrong@Password123}
    driver-class-name: com.microsoft.sqlserver.jdbc.SQLServerDriver
  jpa:
    open-in-view: false
    hibernate:
      ddl-auto: update
      naming:
        # Giữ NGUYÊN tên trong @Table/@Column (StoreAccounts, WatchID...) đúng như đề bài.
        # Mặc định Spring Boot đổi thành store_accounts, watch_id...
        physical-strategy: org.hibernate.boot.model.naming.PhysicalNamingStrategyStandardImpl
    show-sql: false
  cloud:
    openfeign:
      client:
        config:
          default:
            connect-timeout: 2000     # ms - MSBrand tắt -> lỗi nhanh, không treo request
            read-timeout: 5000

# Địa chỉ MSBrand (participant của Saga). Docker: http://ms-brand:8082
brand-service:
  url: ${BRAND_SERVICE_URL:http://localhost:8082}

saga:
  fault-injection:
    # true: cho phép header X-Saga-Fail-After-Step để GIẢ LẬP lỗi khi test/demo Saga.
    # Môi trường production phải đặt false (SAGA_FAULT_INJECTION=false).
    enabled: ${SAGA_FAULT_INJECTION:true}
  compensation:
    max-attempts: 3       # compensation phải "Reliable" -> thử lại tối đa 3 lần
    backoff-ms: 1000

logging:
  level:
    com.mss301.watch.service.saga: INFO
    com.mss301.watch.client: DEBUG   # in ra các lời gọi Feign sang MSBrand (cần Logger.Level trong AppConfig)
```

### TODO-6.2 – `SagaState`, `SagaLog`

```java
package com.mss301.watch.entity;

import com.mss301.watch.service.saga.SagaStatus;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

/** Trạng thái hiện tại của 1 Saga (1 dòng / 1 lần thêm-sửa-xoá). Lịch sử từng bước nằm ở SagaLogs. */
// [TODO-6.2: bảng SagaStates]
@Entity
@Table(name = "SagaStates")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SagaState {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "SagaId", nullable = false, unique = true, length = 36)
    private String sagaId;

    @Column(name = "SagaType", length = 20)
    private String sagaType;            // CREATE_WATCH, UPDATE_WATCH, DELETE_WATCH

    @Column(name = "WatchID")
    private Integer watchId;

    @Enumerated(EnumType.STRING)
    @Column(name = "Status", length = 20)
    private SagaStatus status;          // PENDING -> EXECUTING -> COMPLETED | FAILED -> COMPENSATING -> COMPENSATED

    @Column(name = "CurrentStep", length = 50)
    private String currentStep;

    @Column(name = "Payload", columnDefinition = "NVARCHAR(MAX)")
    private String payload;             // JSON snapshot (dữ liệu trước/sau) để có thể khôi phục

    @Column(name = "FailureReason", length = 1000)
    private String failureReason;

    @Column(name = "CreatedAt")
    private LocalDateTime createdAt;

    @Column(name = "UpdatedAt")
    private LocalDateTime updatedAt;
}
```

```java
package com.mss301.watch.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

/** Nhật ký từng bước của Saga: đây là "bằng chứng" để chứng minh Saga đã chạy / bù trừ thế nào. */
// [TODO-6.2: bảng SagaLogs (nhật ký từng bước)]
@Entity
@Table(name = "SagaLogs")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SagaLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "SagaId", nullable = false, length = 36)
    private String sagaId;

    @Column(name = "StepNo")
    private Integer stepNo;

    @Column(name = "StepName", length = 50)
    private String stepName;            // CREATE_WATCH, ASSIGN_BRAND, DELETE_WATCH, UNASSIGN_BRAND, ...

    @Column(name = "Phase", length = 20)
    private String phase;               // EXECUTE | COMPENSATE | FAULT

    @Column(name = "Result", length = 20)
    private String result;              // SUCCESS | FAILED | TRIGGERED | SKIPPED

    @Column(name = "Message", length = 1000)
    private String message;

    @Column(name = "CreatedAt")
    private LocalDateTime createdAt;
}
```

### TODO-6.3 – `SagaStatus`

```java
package com.mss301.watch.service.saga;

/**
 * 6 trạng thái của Saga (Chapter 06 - Slide 27).
 *
 * <pre>
 * PENDING -> EXECUTING -> COMPLETED                               (thành công)
 *                 \-> FAILED -> COMPENSATING -> COMPENSATED       (thất bại, đã bù trừ xong)
 *                                    \-> (dừng ở COMPENSATING)    (compensation cũng lỗi -> cần xử lý thủ công)
 * </pre>
 */
// [TODO-6.3: 6 trạng thái Saga (Slide 27)]
public enum SagaStatus {
    PENDING,
    EXECUTING,
    COMPLETED,
    FAILED,
    COMPENSATING,
    COMPENSATED
}
```

### TODO-6.4 – `SagaTracker`

```java
package com.mss301.watch.service.saga;

import com.mss301.watch.entity.SagaLog;
import com.mss301.watch.entity.SagaState;
import com.mss301.watch.repository.SagaLogRepository;
import com.mss301.watch.repository.SagaStateRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Ghi trạng thái + nhật ký Saga (State Management - Slide 25, 27).
 * <p>
 * REQUIRES_NEW: mỗi lần ghi là 1 transaction riêng và COMMIT NGAY. Kể cả khi ai đó lỡ bọc
 * orchestrator trong @Transactional rồi bị rollback, nhật ký Saga vẫn còn để điều tra.
 */
// [TODO-6.4: ghi trạng thái/nhật ký bằng REQUIRES_NEW]
@Service
@RequiredArgsConstructor
public class SagaTracker {

    private final SagaStateRepository stateRepository;
    private final SagaLogRepository logRepository;

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public SagaState start(String sagaType, Integer watchId, String payload) {
        LocalDateTime now = LocalDateTime.now();
        return stateRepository.save(SagaState.builder()
            .sagaId(UUID.randomUUID().toString())
            .sagaType(sagaType)
            .watchId(watchId)
            .status(SagaStatus.PENDING)
            .payload(payload)
            .createdAt(now)
            .updatedAt(now)
            .build());
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void updateStatus(String sagaId, SagaStatus status) {
        SagaState s = get(sagaId);
        s.setStatus(status);
        s.setUpdatedAt(LocalDateTime.now());
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void currentStep(String sagaId, String stepName) {
        SagaState s = get(sagaId);
        s.setCurrentStep(stepName);
        s.setUpdatedAt(LocalDateTime.now());
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void attachWatch(String sagaId, Integer watchId) {
        get(sagaId).setWatchId(watchId);
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void fail(String sagaId, String reason) {
        SagaState s = get(sagaId);
        s.setStatus(SagaStatus.FAILED);
        s.setFailureReason(truncate(reason));
        s.setUpdatedAt(LocalDateTime.now());
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void log(String sagaId, int stepNo, String stepName, String phase, String result, String message) {
        logRepository.save(SagaLog.builder()
            .sagaId(sagaId)
            .stepNo(stepNo)
            .stepName(stepName)
            .phase(phase)
            .result(result)
            .message(truncate(message))
            .createdAt(LocalDateTime.now())
            .build());
    }

    private SagaState get(String sagaId) {
        return stateRepository.findBySagaId(sagaId)
            .orElseThrow(() -> new IllegalStateException("Saga not found: " + sagaId));
    }

    private String truncate(String s) {
        return s == null || s.length() <= 1000 ? s : s.substring(0, 1000);
    }
}
```

### TODO-6.5 – `WatchLocalService`

```java
package com.mss301.watch.service;

import com.mss301.watch.entity.Watch;
import com.mss301.watch.repository.WatchCategoryRepository;
import com.mss301.watch.repository.WatchRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

/**
 * Các LOCAL TRANSACTION của MSWatch trên DBWatch.
 * Mỗi method có @Transactional riêng -> commit ngay khi method kết thúc (ACID trong phạm vi 1 database).
 */
// [TODO-6.5: các local transaction trên DBWatch]
@Service
@RequiredArgsConstructor
@Slf4j
public class WatchLocalService {

    private final WatchRepository watchRepository;
    private final WatchCategoryRepository categoryRepository;

    @Transactional(readOnly = true)
    public WatchData load(Integer id) {
        return watchRepository.findById(id)
            .map(WatchData::from)
            .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Watch not found with id: " + id));
    }

    /** Bước CREATE_WATCH. */
    @Transactional
    public Integer insert(WatchData d) {
        Watch w = new Watch();
        apply(w, d);
        Integer id = watchRepository.save(w).getWatchId();
        log.info("[LOCAL TX] INSERT watch id={} brand={}", id, d.brandId());
        return id;
    }

    /** Bước UPDATE_WATCH và cũng là compensation RESTORE_WATCH (ghi lại dữ liệu snapshot). */
    @Transactional
    public void update(WatchData d) {
        Watch w = watchRepository.findById(d.watchId())
            .orElseThrow(() -> new IllegalStateException("Watch " + d.watchId() + " no longer exists"));
        apply(w, d);                       // dirty checking -> UPDATE khi commit
        log.info("[LOCAL TX] UPDATE watch id={} brand={} name='{}'", d.watchId(), d.brandId(), d.name());
    }

    /** Compensation DELETE_WATCH - IDEMPOTENT: gọi lại nhiều lần vẫn an toàn. */
    @Transactional
    public void deleteIfExists(Integer id) {
        if (id != null && watchRepository.existsById(id)) {
            watchRepository.deleteById(id);
            log.info("[LOCAL TX] DELETE watch id={} (compensation)", id);
        }
    }

    /** Bước DELETE_WATCH (pivot của saga xoá). */
    @Transactional
    public void delete(Integer id) {
        Watch w = watchRepository.findById(id)
            .orElseThrow(() -> new IllegalStateException("Watch " + id + " no longer exists"));
        watchRepository.delete(w);
        log.info("[LOCAL TX] DELETE watch id={}", id);
    }

    private void apply(Watch w, WatchData d) {
        w.setName(d.name());
        w.setCategory(categoryRepository.getReferenceById(d.categoryId()));
        w.setBrandId(d.brandId());
        w.setCaseMaterial(d.caseMaterial());
        w.setStrapMaterial(d.strapMaterial());
        w.setWaterpMaterial(d.waterpMaterial());
        w.setPrice(d.price());
        w.setReleaseDate(d.releaseDate());
        w.setStock(d.stock());
    }
}
```

### TODO-6.6 – `WatchData`

```java
package com.mss301.watch.service;

import com.mss301.watch.dto.WatchRequest;
import com.mss301.watch.entity.Watch;

import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * Bản chụp (snapshot) dữ liệu của 1 watch, không phụ thuộc JPA.
 * Dùng làm input cho các bước Saga và làm dữ liệu khôi phục (RESTORE) khi compensate.
 */
// [TODO-6.6: snapshot dữ liệu để RESTORE]
public record WatchData(
    Integer watchId,
    String name,
    Integer categoryId,
    Integer brandId,
    String caseMaterial,
    String strapMaterial,
    String waterpMaterial,
    BigDecimal price,
    LocalDate releaseDate,
    Integer stock
) {
    public static WatchData from(Watch w) {
        return new WatchData(w.getWatchId(), w.getName(),
            w.getCategory() != null ? w.getCategory().getCategoryId() : null,
            w.getBrandId(), w.getCaseMaterial(), w.getStrapMaterial(), w.getWaterpMaterial(),
            w.getPrice(), w.getReleaseDate(), w.getStock());
    }

    public static WatchData from(WatchRequest r, Integer watchId) {
        return new WatchData(watchId, r.getName(), r.getCategoryId(), r.getBrandId(),
            r.getCaseMaterial(), r.getStrapMaterial(), r.getWaterpMaterial(),
            r.getPrice(), r.getReleaseDate(), r.getStock());
    }
}
```

### TODO-6.7 – Feign client

`MSWatchApplication` có `@EnableFeignClients`.

```java
package com.mss301.watch.client;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;

/**
 * Client gọi các LOCAL TRANSACTION của participant MSBrand.
 * - HTTP 4xx/5xx  -> FeignException (VD: FeignException.NotFound khi brand không tồn tại)
 * - MSBrand tắt    -> RetryableException (status = -1)
 * Orchestrator bắt các exception này để quyết định compensate.
 */
// [TODO-6.7: Feign gọi API nội bộ của MSBrand]
@FeignClient(name = "ms-brand", url = "${brand-service.url}")
public interface BrandServiceClient {

    /** Gán watch vào brand (idempotent). Dùng làm bước Saga và cũng làm compensation. */
    @PutMapping("/internal/brands/{brandId}/watches/{watchId}")
    void assignWatch(@PathVariable("brandId") Integer brandId, @PathVariable("watchId") Integer watchId);

    /** Gỡ watch khỏi brand (idempotent). */
    @DeleteMapping("/internal/brands/watches/{watchId}")
    void unassignWatch(@PathVariable("watchId") Integer watchId);
}
```

### TODO-6.8 – `SagaStep`

```java
package com.mss301.watch.service.saga;

/**
 * Một bước của Saga = 1 local transaction (action) + 1 compensating transaction (compensation).
 * <p>
 * Bước KHÔNG có compensation gọi là <b>pivot</b>: khi pivot đã commit thì Saga không thể quay lui nữa,
 * chỉ có thể đi tiếp tới COMPLETED. Vì vậy pivot luôn được đặt ở CUỐI chuỗi.
 */
// [TODO-6.8: bước Saga = action + compensation; pivot]
public record SagaStep(String name, Runnable action, String compensationName, Runnable compensation) {

    public static SagaStep of(String name, Runnable action, String compensationName, Runnable compensation) {
        return new SagaStep(name, action, compensationName, compensation);
    }

    public static SagaStep pivot(String name, Runnable action) {
        return new SagaStep(name, action, null, null);
    }

    public boolean isPivot() {
        return compensation == null;
    }
}
```

### TODO-6.9, TODO-6.10, TODO-6.11 – ⭐ `WatchSagaOrchestrator`

```java
package com.mss301.watch.service.saga;

import com.mss301.watch.client.BrandServiceClient;
import com.mss301.watch.service.WatchData;
import com.mss301.watch.service.WatchLocalService;
import feign.FeignException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import tools.jackson.databind.json.JsonMapper;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicReference;

/**
 * SAGA ORCHESTRATOR (Chapter 06 - Slide 24).
 * <p>
 * Điều phối 3 nghiệp vụ, mỗi nghiệp vụ chạm vào 2 database của 2 service:
 * <pre>
 * CREATE_WATCH : [1] CREATE_WATCH   (DBWatch)  ↔ DELETE_WATCH
 *                [2] ASSIGN_BRAND   (DBBrand)  ↔ UNASSIGN_BRAND
 * UPDATE_WATCH : [1] UPDATE_WATCH   (DBWatch)  ↔ RESTORE_WATCH (từ snapshot)
 *                [2] ASSIGN_BRAND   (DBBrand)  ↔ ASSIGN_BRAND_BACK (gán lại brand cũ)
 * DELETE_WATCH : [1] UNASSIGN_BRAND (DBBrand)  ↔ ASSIGN_BRAND_BACK
 *                [2] DELETE_WATCH   (DBWatch)  ↔ (không có - PIVOT)
 * </pre>
 *
 * QUY TẮC QUAN TRỌNG:
 * <ol>
 *   <li>KHÔNG đặt @Transactional ở class này: mỗi bước đã là 1 local transaction riêng (WatchLocalService /
 *       MSBrand). Một @Transactional bao ngoài không rollback được DBBrand, lại giữ connection DB trong lúc gọi mạng.</li>
 *   <li>Chỉ những bước ĐÃ commit mới được đưa vào stack và bù trừ theo thứ tự NGƯỢC (LIFO).</li>
 *   <li>Lỗi từ MSBrand (404, service down) KHÔNG được "nuốt" bằng fallback lưu dữ liệu tạm: Saga phải compensate.</li>
 * </ol>
 */
// [TODO-6.9, TODO-6.10, TODO-6.11: Saga Orchestrator]
@Service
@RequiredArgsConstructor
@Slf4j
public class WatchSagaOrchestrator {

    private final WatchLocalService localService;
    private final BrandServiceClient brandClient;
    private final SagaTracker tracker;
    private final SagaFaultInjector faultInjector;
    private final JsonMapper jsonMapper;       // Jackson 3 (Boot 4)

    @Value("${saga.compensation.max-attempts:3}")
    private int maxAttempts;

    @Value("${saga.compensation.backoff-ms:1000}")
    private long backoffMs;

    // =========================================================================================
    // 1) CREATE: lưu watch (DBWatch) -> gán watch vào brand (DBBrand)
    // =========================================================================================
    // [TODO-6.11a: Saga CREATE_WATCH]
    public SagaOutcome createWatch(WatchData data, Integer failAfterStep) {
        String sagaId = tracker.start("CREATE_WATCH", null, toJson(Map.of("after", data))).getSagaId();
        AtomicReference<Integer> watchId = new AtomicReference<>();   // bước 1 sinh ra id, bước 2 dùng lại

        List<SagaStep> steps = List.of(
            SagaStep.of("CREATE_WATCH",
                () -> {
                    watchId.set(localService.insert(data));
                    tracker.attachWatch(sagaId, watchId.get());
                },
                "DELETE_WATCH",
                () -> localService.deleteIfExists(watchId.get())),

            SagaStep.of("ASSIGN_BRAND",
                () -> brandClient.assignWatch(data.brandId(), watchId.get()),
                "UNASSIGN_BRAND",
                () -> brandClient.unassignWatch(watchId.get()))
        );

        execute(sagaId, steps, failAfterStep);
        return new SagaOutcome(sagaId, watchId.get(), SagaStatus.COMPLETED);
    }

    // =========================================================================================
    // 2) UPDATE: cập nhật watch (DBWatch) -> chuyển watch sang brand mới (DBBrand)
    // =========================================================================================
    // [TODO-6.11b: Saga UPDATE_WATCH]
    public SagaOutcome updateWatch(WatchData before, WatchData after, Integer failAfterStep) {
        Integer id = before.watchId();
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("before", before);           // snapshot để RESTORE nếu thất bại
        payload.put("after", after);
        String sagaId = tracker.start("UPDATE_WATCH", id, toJson(payload)).getSagaId();

        List<SagaStep> steps = List.of(
            SagaStep.of("UPDATE_WATCH",
                () -> localService.update(after),
                "RESTORE_WATCH",
                () -> localService.update(before)),

            SagaStep.of("ASSIGN_BRAND",
                () -> brandClient.assignWatch(after.brandId(), id),
                "ASSIGN_BRAND_BACK",
                () -> brandClient.assignWatch(before.brandId(), id))
        );

        execute(sagaId, steps, failAfterStep);
        return new SagaOutcome(sagaId, id, SagaStatus.COMPLETED);
    }

    // =========================================================================================
    // 3) DELETE: gỡ watch khỏi brand (DBBrand) -> xoá watch (DBWatch, PIVOT)
    //    Thứ tự này có chủ ý: bước "xoá cứng" khó hoàn tác (IDENTITY sinh id mới) nên đặt CUỐI làm pivot.
    // =========================================================================================
    // [TODO-6.11c: Saga DELETE_WATCH (pivot cuối)]
    public SagaOutcome deleteWatch(WatchData before, Integer failAfterStep) {
        Integer id = before.watchId();
        String sagaId = tracker.start("DELETE_WATCH", id, toJson(Map.of("before", before))).getSagaId();

        List<SagaStep> steps = List.of(
            SagaStep.of("UNASSIGN_BRAND",
                () -> brandClient.unassignWatch(id),
                "ASSIGN_BRAND_BACK",
                () -> brandClient.assignWatch(before.brandId(), id)),

            SagaStep.pivot("DELETE_WATCH",
                () -> localService.delete(id))
        );

        execute(sagaId, steps, failAfterStep);
        return new SagaOutcome(sagaId, id, SagaStatus.COMPLETED);
    }

    // =========================================================================================
    // "Động cơ" Saga dùng chung cho cả 3 nghiệp vụ
    // =========================================================================================
    // [TODO-6.9: động cơ Saga - stack LIFO, không @Transactional]
    private void execute(String sagaId, List<SagaStep> steps, Integer failAfterStep) {
        tracker.updateStatus(sagaId, SagaStatus.EXECUTING);
        Deque<CompletedStep> completed = new ArrayDeque<>();   // STACK các bước đã commit
        int stepNo = 0;
        String currentStep = null;

        try {
            for (SagaStep step : steps) {
                stepNo++;
                currentStep = step.name();
                tracker.currentStep(sagaId, step.name());

                step.action().run();                           // 1 local transaction (ở DBWatch hoặc DBBrand)

                tracker.log(sagaId, stepNo, step.name(), "EXECUTE", "SUCCESS",
                    step.isPivot() ? "Pivot committed - saga can only move forward now" : "Local transaction committed");
                log.info("[SAGA {}] step {} {} -> SUCCESS", sagaId, stepNo, step.name());

                if (!step.isPivot()) {
                    completed.push(new CompletedStep(stepNo, step));
                }

                if (faultInjector.shouldFailAfter(failAfterStep, stepNo)) {
                    if (step.isPivot()) {
                        // Sau pivot không còn gì để quay lui -> bỏ qua lỗi giả, Saga phải đi tới COMPLETED
                        tracker.log(sagaId, stepNo, "FAULT_INJECTION", "FAULT", "SKIPPED",
                            "Ignored: step " + stepNo + " (" + step.name() + ") is the pivot, saga cannot be rolled back");
                    } else {
                        currentStep = "FAULT_INJECTION after " + step.name();
                        throw new SimulatedSagaFailureException(
                            "Simulated failure after step " + stepNo + " (" + step.name() + ")");
                    }
                }
            }

            tracker.updateStatus(sagaId, SagaStatus.COMPLETED);
            log.info("[SAGA {}] COMPLETED", sagaId);

        } catch (RuntimeException ex) {
            String reason = describe(ex);
            if (ex instanceof SimulatedSagaFailureException) {
                tracker.log(sagaId, stepNo, "FAULT_INJECTION", "FAULT", "TRIGGERED", reason);
            } else {
                tracker.log(sagaId, stepNo, currentStep, "EXECUTE", "FAILED", reason);
            }
            log.warn("[SAGA {}] FAILED at {}: {}", sagaId, currentStep, reason);
            tracker.fail(sagaId, reason);                                          // FAILED

            boolean allCompensated = compensate(sagaId, completed);                // COMPENSATING
            SagaStatus finalStatus = allCompensated ? SagaStatus.COMPENSATED : SagaStatus.COMPENSATING;
            tracker.updateStatus(sagaId, finalStatus);
            log.warn("[SAGA {}] finished with status {}", sagaId, finalStatus);

            throw new SagaExecutionException(sagaId, finalStatus, currentStep, httpStatusFor(ex), reason, ex);
        }
    }

    /** Bù trừ các bước đã commit theo thứ tự NGƯỢC. Dừng lại nếu một compensation vẫn lỗi sau khi retry. */
    // [TODO-6.10: compensation theo thứ tự ngược, dừng ở COMPENSATING nếu lỗi]
    private boolean compensate(String sagaId, Deque<CompletedStep> completed) {
        tracker.updateStatus(sagaId, SagaStatus.COMPENSATING);
        while (!completed.isEmpty()) {
            CompletedStep done = completed.pop();                                  // LIFO
            if (!compensateWithRetry(sagaId, done)) {
                tracker.log(sagaId, done.stepNo(), "COMPENSATION_HALTED", "COMPENSATE", "FAILED",
                    completed.size() + " earlier step(s) still need compensation - manual intervention required");
                log.error("[SAGA {}] compensation halted at step {}, saga stays COMPENSATING", sagaId, done.stepNo());
                return false;
            }
        }
        return true;
    }

    /** Compensation phải "Reliable" (Slide 25): thử lại vài lần. Nhờ IDEMPOTENT nên retry an toàn. */
    // [TODO-6.10: retry compensation]
    private boolean compensateWithRetry(String sagaId, CompletedStep done) {
        SagaStep step = done.step();
        for (int attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                step.compensation().run();
                tracker.log(sagaId, done.stepNo(), step.compensationName(), "COMPENSATE", "SUCCESS",
                    "Undo " + step.name() + " (attempt " + attempt + ")");
                log.info("[SAGA {}] compensate step {} {} -> SUCCESS", sagaId, done.stepNo(), step.compensationName());
                return true;
            } catch (RuntimeException ex) {
                tracker.log(sagaId, done.stepNo(), step.compensationName(), "COMPENSATE", "FAILED",
                    "Attempt " + attempt + "/" + maxAttempts + ": " + describe(ex));
                sleep(backoffMs);
            }
        }
        return false;
    }

    // ===================================== helpers =====================================

    // [TODO-6.15: phân loại lỗi Feign (404 / unreachable)]
    private String describe(RuntimeException ex) {
        if (ex instanceof FeignException fe) {
            if (fe.status() == 404) {
                return "MSBrand returned 404: " + remoteMessage(fe, "brand not found");
            }
            if (fe.status() < 0) {                       // RetryableException: không kết nối được
                return "MSBrand is unreachable: " + fe.getMessage();
            }
            return "MSBrand returned HTTP " + fe.status() + ": " + remoteMessage(fe, fe.getMessage());
        }
        return ex.getClass().getSimpleName() + ": " + ex.getMessage();
    }

    /** Lấy trường "message" trong ApiResponse lỗi do MSBrand trả về. */
    private String remoteMessage(FeignException fe, String fallback) {
        try {
            String body = fe.contentUTF8();
            if (body != null && !body.isBlank()) {
                var node = jsonMapper.readTree(body).get("message");
                if (node != null && !node.isNull()) {
                    return node.asString();
                }
            }
        } catch (RuntimeException ignored) {
            // body không phải JSON -> dùng fallback
        }
        return fallback;
    }

    private HttpStatus httpStatusFor(RuntimeException ex) {
        if (ex instanceof FeignException fe) {
            if (fe.status() == 404) return HttpStatus.BAD_REQUEST;              // dữ liệu không hợp lệ (brand không tồn tại)
            if (fe.status() < 0 || fe.status() >= 500) return HttpStatus.SERVICE_UNAVAILABLE;
        }
        return HttpStatus.INTERNAL_SERVER_ERROR;                                 // gồm cả lỗi giả lập
    }

    private String toJson(Object value) {
        return jsonMapper.writeValueAsString(value);                             // Jackson 3: unchecked exception
    }

    private void sleep(long ms) {
        try {
            Thread.sleep(ms);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    private record CompletedStep(int stepNo, SagaStep step) {
    }
}
```

**Đọc hiểu theo 5 câu hỏi:**

1. **Vì sao không có `@Transactional`?** Nếu có, khi bước 2 lỗi thì Spring rollback DBWatch, nhưng nếu MSBrand đã commit thì DBBrand vẫn giữ thay đổi → mất nhất quán. Ngoài ra transaction sẽ giữ connection DB trong suốt thời gian chờ mạng.
2. **Stack `completed` để làm gì?** Mỗi bước commit xong thì được `push` vào stack. Khi lỗi, `pop` lần lượt nên compensation chạy theo thứ tự **ngược** (LIFO). Bước lỗi **không** nằm trong stack vì nó chưa commit.
3. **Vì sao retry compensation?** Slide 25 yêu cầu compensation phải *Reliable*. Lỗi mạng tạm thời sẽ được thử lại tối đa 3 lần. Retry an toàn vì các compensation đều *Idempotent*.
4. **Nếu compensation vẫn lỗi?** Saga **dừng ở `COMPENSATING`** và ghi `COMPENSATION_HALTED`, không báo `COMPENSATED` sai sự thật. Các bước còn lại để nguyên (không bù trừ "nhảy cóc") để có thể xử lý tiếp đúng thứ tự.
5. **Vì sao MSWatch không dùng Circuit Breaker fallback?** Fallback kiểu "lưu watch mà không qua MSBrand" chính là bỏ qua tính nhất quán, ngược với mục đích của Saga (anti-pattern #1). Circuit Breaker vẫn được dùng ở Gateway để trả lỗi nhanh khi một service sập.

### TODO-6.12 – Fault injection

```java
package com.mss301.watch.service.saga;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/**
 * Fault injection cho mục đích HỌC TẬP: client gửi header "X-Saga-Fail-After-Step: N"
 * -> Saga sẽ ném lỗi giả ngay SAU khi bước N commit thành công.
 * <p>
 * Nhờ vậy có thể chứng minh: các bước đã commit (kể cả ở MSBrand) đều được bù trừ theo thứ tự ngược.
 * Tắt bằng saga.fault-injection.enabled=false.
 */
// [TODO-6.12: fault injection để chứng minh compensation]
@Component
@Slf4j
public class SagaFaultInjector {

    @Value("${saga.fault-injection.enabled:false}")
    private boolean enabled;

    public boolean shouldFailAfter(Integer failAfterStep, int completedStepNo) {
        if (failAfterStep == null) {
            return false;
        }
        if (!enabled) {
            log.warn("Header X-Saga-Fail-After-Step={} ignored because saga.fault-injection.enabled=false", failAfterStep);
            return false;
        }
        return failAfterStep == completedStepNo;
    }
}
```

```java
package com.mss301.watch.service.saga;

/** Lỗi GIẢ LẬP (fault injection) - chỉ dùng để test/demo cơ chế compensation. */
// [TODO-6.12]
public class SimulatedSagaFailureException extends RuntimeException {
    public SimulatedSagaFailureException(String message) {
        super(message);
    }
}
```

### TODO-6.13 – Validation + `WatchService`

```java
package com.mss301.watch.dto;

import jakarta.validation.constraints.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;

// [TODO-6.13: ràng buộc name > 10 ký tự, price >= 100, đủ field]
@Data
public class WatchRequest {

    @NotBlank(message = "Name is required")
    @Size(min = 11, message = "Name must be longer than 10 characters")
    private String name;

    @NotNull(message = "CategoryId is required")
    private Integer categoryId;

    @NotNull(message = "BrandId is required")
    private Integer brandId;

    @NotBlank(message = "CaseMaterial is required")
    private String caseMaterial;

    @NotBlank(message = "StrapMaterial is required")
    private String strapMaterial;

    @NotBlank(message = "WaterpMaterial is required")
    private String waterpMaterial;

    @NotNull(message = "Price is required")
    @DecimalMin(value = "100.0", message = "Price must be at least 100")
    private BigDecimal price;

    @NotNull(message = "ReleaseDate is required")
    private LocalDate releaseDate;

    @NotNull(message = "Stock is required")
    @Min(value = 0, message = "Stock must be >= 0")
    private Integer stock;
}
```

```java
package com.mss301.watch.service;

import com.mss301.watch.dto.WatchRequest;
import com.mss301.watch.dto.WatchResponse;
import com.mss301.watch.entity.Watch;
import com.mss301.watch.repository.WatchCategoryRepository;
import com.mss301.watch.repository.WatchRepository;
import com.mss301.watch.service.saga.SagaOutcome;
import com.mss301.watch.service.saga.WatchSagaOrchestrator;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.time.LocalDate;
import java.util.List;

/**
 * Business service: kiểm tra nghiệp vụ TRƯỚC khi chạy Saga (validate rẻ, không cần compensate),
 * sau đó giao cho WatchSagaOrchestrator thực hiện các bước phân tán.
 */
// [TODO-6.13: validate nghiệp vụ TRƯỚC khi chạy Saga]
@Service
@RequiredArgsConstructor
public class WatchService {

    private final WatchRepository watchRepository;
    private final WatchCategoryRepository categoryRepository;
    private final WatchLocalService localService;
    private final WatchSagaOrchestrator sagaOrchestrator;

    /** Watch mới nhất ở đầu danh sách (ORDER BY WatchID DESC). */
    // [TODO-6.13: watch mới ở đầu danh sách]
    public List<WatchResponse> findAll() {
        return watchRepository.findAllByOrderByWatchIdDesc().stream()
            .map(this::toResponse).toList();
    }

    public SagaResult<WatchResponse> create(WatchRequest request, Integer failAfterStep) {
        validate(request);
        SagaOutcome outcome = sagaOrchestrator.createWatch(WatchData.from(request, null), failAfterStep);
        return new SagaResult<>(outcome.sagaId(), loadResponse(outcome.watchId()));
    }

    public SagaResult<WatchResponse> update(Integer id, WatchRequest request, Integer failAfterStep) {
        WatchData before = localService.load(id);          // 404 nếu không có
        validate(request);
        SagaOutcome outcome = sagaOrchestrator.updateWatch(before, WatchData.from(request, id), failAfterStep);
        return new SagaResult<>(outcome.sagaId(), loadResponse(id));
    }

    public SagaResult<Void> delete(Integer id, Integer failAfterStep) {
        WatchData before = localService.load(id);
        SagaOutcome outcome = sagaOrchestrator.deleteWatch(before, failAfterStep);
        return new SagaResult<>(outcome.sagaId(), null);
    }

    // [TODO-6.13]
    private void validate(WatchRequest request) {
        if (!LocalDate.now().equals(request.getReleaseDate())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                "Release date must be today's date: " + LocalDate.now());
        }
        if (!categoryRepository.existsById(request.getCategoryId())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                "Category not found with id: " + request.getCategoryId());
        }
        // Brand KHÔNG kiểm tra ở đây: brand thuộc MSBrand -> được xác nhận trong bước ASSIGN_BRAND của Saga.
    }

    private WatchResponse loadResponse(Integer id) {
        return watchRepository.findById(id).map(this::toResponse)
            .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Watch not found with id: " + id));
    }

    private WatchResponse toResponse(Watch w) {
        return WatchResponse.builder()
            .watchId(w.getWatchId())
            .name(w.getName())
            .categoryId(w.getCategory() != null ? w.getCategory().getCategoryId() : null)
            .categoryName(w.getCategory() != null ? w.getCategory().getCategoryName() : null)
            .brandId(w.getBrandId())
            .caseMaterial(w.getCaseMaterial())
            .strapMaterial(w.getStrapMaterial())
            .waterpMaterial(w.getWaterpMaterial())
            .price(w.getPrice())
            .releaseDate(w.getReleaseDate())
            .stock(w.getStock())
            .build();
    }
}
```

### TODO-6.14 – Controllers

```java
package com.mss301.watch.controller;

import com.mss301.watch.dto.ApiResponse;
import com.mss301.watch.dto.WatchRequest;
import com.mss301.watch.dto.WatchResponse;
import com.mss301.watch.service.SagaResult;
import com.mss301.watch.service.WatchService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;

// [TODO-6.14: CRUD /api/watches, header X-Saga-Id, X-Saga-Fail-After-Step, kiểm tra role]
@RestController
@RequestMapping("/api/watches")
@RequiredArgsConstructor
@Tag(name = "Watch", description = "Watch management with Saga Pattern")
public class WatchController {

    /** Header dùng để GIẢ LẬP lỗi sau bước N của Saga (chỉ khi saga.fault-injection.enabled=true). */
    public static final String FAIL_AFTER_HEADER = "X-Saga-Fail-After-Step";
    public static final String SAGA_ID_HEADER = "X-Saga-Id";

    private final WatchService watchService;

    @GetMapping
    @Operation(summary = "List all watches (public, newest first)")
    public ResponseEntity<ApiResponse<List<WatchResponse>>> findAll() {
        return ResponseEntity.ok(ApiResponse.success(watchService.findAll(), "Success"));
    }

    @PostMapping
    @Operation(summary = "Add a new watch (Admin only) - runs CREATE_WATCH saga")
    public ResponseEntity<ApiResponse<WatchResponse>> create(
            @RequestHeader(value = "X-User-Role", required = false) String role,
            @Parameter(description = "Test only: fail after step N")
            @RequestHeader(value = FAIL_AFTER_HEADER, required = false) Integer failAfterStep,
            @Valid @RequestBody WatchRequest request) {
        checkAdminRole(role);
        SagaResult<WatchResponse> result = watchService.create(request, failAfterStep);
        return ResponseEntity.status(HttpStatus.CREATED)
            .header(SAGA_ID_HEADER, result.sagaId())
            .body(ApiResponse.success(result.body(), "Watch created successfully (saga " + result.sagaId() + " COMPLETED)"));
    }

    @PutMapping("/{id}")
    @Operation(summary = "Update a watch (Admin only) - runs UPDATE_WATCH saga")
    public ResponseEntity<ApiResponse<WatchResponse>> update(
            @RequestHeader(value = "X-User-Role", required = false) String role,
            @RequestHeader(value = FAIL_AFTER_HEADER, required = false) Integer failAfterStep,
            @PathVariable Integer id,
            @Valid @RequestBody WatchRequest request) {
        checkAdminRole(role);
        SagaResult<WatchResponse> result = watchService.update(id, request, failAfterStep);
        return ResponseEntity.ok()
            .header(SAGA_ID_HEADER, result.sagaId())
            .body(ApiResponse.success(result.body(), "Watch updated successfully (saga " + result.sagaId() + " COMPLETED)"));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Delete a watch (Admin only) - runs DELETE_WATCH saga")
    public ResponseEntity<ApiResponse<Void>> delete(
            @RequestHeader(value = "X-User-Role", required = false) String role,
            @RequestHeader(value = FAIL_AFTER_HEADER, required = false) Integer failAfterStep,
            @PathVariable Integer id) {
        checkAdminRole(role);
        SagaResult<Void> result = watchService.delete(id, failAfterStep);
        return ResponseEntity.ok()
            .header(SAGA_ID_HEADER, result.sagaId())
            .body(ApiResponse.success(null, "Watch deleted successfully (saga " + result.sagaId() + " COMPLETED)"));
    }

    // [TODO-6.14: chỉ Admin (role=1)]
    static void checkAdminRole(String role) {
        if (!"1".equals(role)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN,
                "Only Administrator (role=1) can perform this action");
        }
    }
}
```

```java
package com.mss301.watch.controller;

import com.mss301.watch.dto.ApiResponse;
import com.mss301.watch.dto.SagaResponse;
import com.mss301.watch.entity.SagaState;
import com.mss301.watch.repository.SagaLogRepository;
import com.mss301.watch.repository.SagaStateRepository;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;

/** Xem trạng thái + nhật ký Saga để CHỨNG MINH Saga đã chạy / bù trừ thế nào (Admin only). */
// [TODO-6.14: GET /api/sagas, /api/sagas/{sagaId}]
@RestController
@RequestMapping("/api/sagas")
@RequiredArgsConstructor
@Tag(name = "Saga", description = "Saga state & step logs (for testing/monitoring)")
public class SagaController {

    private final SagaStateRepository stateRepository;
    private final SagaLogRepository logRepository;

    @GetMapping
    @Operation(summary = "Các saga gần nhất (mới nhất trước)")
    public ResponseEntity<ApiResponse<List<SagaResponse>>> recent(
            @RequestHeader(value = "X-User-Role", required = false) String role,
            @RequestParam(defaultValue = "20") int limit) {
        WatchController.checkAdminRole(role);
        List<SagaResponse> list = stateRepository.findAllByOrderByIdDesc(PageRequest.of(0, Math.min(limit, 100)))
            .stream().map(s -> SagaResponse.of(s, null)).toList();
        return ResponseEntity.ok(ApiResponse.success(list, "Success"));
    }

    @GetMapping("/{sagaId}")
    @Operation(summary = "Chi tiết 1 saga kèm từng bước EXECUTE / COMPENSATE")
    public ResponseEntity<ApiResponse<SagaResponse>> detail(
            @RequestHeader(value = "X-User-Role", required = false) String role,
            @PathVariable String sagaId) {
        WatchController.checkAdminRole(role);
        SagaState state = stateRepository.findBySagaId(sagaId)
            .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Saga not found: " + sagaId));
        return ResponseEntity.ok(ApiResponse.success(
            SagaResponse.of(state, logRepository.findBySagaIdOrderByIdAsc(sagaId)), "Success"));
    }
}
```

```java
package com.mss301.watch.dto;

import com.mss301.watch.entity.SagaLog;
import com.mss301.watch.entity.SagaState;
import com.mss301.watch.service.saga.SagaStatus;

import java.time.LocalDateTime;
import java.util.List;

// [TODO-6.14]
public record SagaResponse(
    String sagaId,
    String sagaType,
    Integer watchId,
    SagaStatus status,
    String currentStep,
    String failureReason,
    String payload,
    LocalDateTime createdAt,
    LocalDateTime updatedAt,
    List<StepLog> steps
) {
    public record StepLog(Integer stepNo, String stepName, String phase, String result, String message, LocalDateTime at) {
    }

    public static SagaResponse of(SagaState s, List<SagaLog> logs) {
        List<StepLog> steps = logs == null ? null : logs.stream()
            .map(l -> new StepLog(l.getStepNo(), l.getStepName(), l.getPhase(), l.getResult(), l.getMessage(), l.getCreatedAt()))
            .toList();
        return new SagaResponse(s.getSagaId(), s.getSagaType(), s.getWatchId(), s.getStatus(), s.getCurrentStep(),
            s.getFailureReason(), s.getPayload(), s.getCreatedAt(), s.getUpdatedAt(), steps);
    }
}
```

### TODO-6.15 – Exception

```java
package com.mss301.watch.service.saga;

import lombok.Getter;
import org.springframework.http.HttpStatus;

/** Ném ra khi Saga thất bại (sau khi đã chạy compensation). GlobalExceptionHandler chuyển thành HTTP response. */
// [TODO-6.15]
@Getter
public class SagaExecutionException extends RuntimeException {

    private final String sagaId;
    private final SagaStatus sagaStatus;   // COMPENSATED hoặc COMPENSATING (nếu compensation lỗi)
    private final String failedStep;
    private final HttpStatus httpStatus;
    private final String reason;

    public SagaExecutionException(String sagaId, SagaStatus sagaStatus, String failedStep,
                                  HttpStatus httpStatus, String reason, Throwable cause) {
        super("Saga " + sagaId + " " + sagaStatus + " - failed at " + failedStep + ": " + reason, cause);
        this.sagaId = sagaId;
        this.sagaStatus = sagaStatus;
        this.failedStep = failedStep;
        this.httpStatus = httpStatus;
        this.reason = reason;
    }
}
```

```java
package com.mss301.watch.exception;

import com.mss301.watch.dto.ApiResponse;
import com.mss301.watch.service.saga.SagaExecutionException;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.server.ResponseStatusException;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.stream.Collectors;

// [TODO-6.15: chuyển SagaExecutionException / validation thành HTTP response]
@RestControllerAdvice
public class GlobalExceptionHandler {

    /** Saga thất bại: trả về sagaId + trạng thái cuối để client tra cứu GET /api/sagas/{sagaId}. */
    @ExceptionHandler(SagaExecutionException.class)
    public ResponseEntity<ApiResponse<Map<String, Object>>> handleSaga(SagaExecutionException ex) {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("sagaId", ex.getSagaId());
        data.put("sagaStatus", ex.getSagaStatus());
        data.put("failedStep", ex.getFailedStep());
        data.put("reason", ex.getReason());
        return ResponseEntity.status(ex.getHttpStatus())
            .header("X-Saga-Id", ex.getSagaId())
            .body(ApiResponse.<Map<String, Object>>builder()
                .success(false)
                .message("Saga " + ex.getSagaStatus() + ": " + ex.getReason())
                .data(data)
                .build());
    }

    @ExceptionHandler(ResponseStatusException.class)
    public ResponseEntity<ApiResponse<Void>> handleResponseStatus(ResponseStatusException ex) {
        return ResponseEntity.status(ex.getStatusCode())
            .body(ApiResponse.error(ex.getReason()));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse<Void>> handleValidation(MethodArgumentNotValidException ex) {
        String message = ex.getBindingResult().getFieldErrors().stream()
            .map(e -> e.getField() + ": " + e.getDefaultMessage())
            .collect(Collectors.joining(", "));
        return ResponseEntity.badRequest().body(ApiResponse.error(message));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleGeneral(Exception ex) {
        return ResponseEntity.internalServerError()
            .body(ApiResponse.error("Internal error: " + ex.getMessage()));
    }
}
```

### TODO-6.16 – Entity `Watch` + seed

```java
package com.mss301.watch.entity;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDate;

// [TODO-6.16: entity Watches (BrandID chỉ là tham chiếu, không join)]
@Entity
@Table(name = "Watches")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Watch {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "WatchID")
    private Integer watchId;

    @Column(name = "Name", nullable = false, length = 255)
    private String name;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "CategoryID")
    private WatchCategory category;

    @Column(name = "BrandID")
    private Integer brandId; // Reference only, no join (Database per Service)

    @Column(name = "CaseMaterial", length = 100)
    private String caseMaterial;

    @Column(name = "StrapMaterial", length = 100)
    private String strapMaterial;

    @Column(name = "WaterpMaterial", length = 50)
    private String waterpMaterial;

    @Column(name = "Price", precision = 10, scale = 2)
    private BigDecimal price;

    @Column(name = "ReleaseDate")
    private LocalDate releaseDate;

    @Column(name = "Stock")
    private Integer stock;
}
```

```java
package com.mss301.watch;

import com.mss301.watch.entity.Watch;
import com.mss301.watch.entity.WatchCategory;
import com.mss301.watch.repository.WatchCategoryRepository;
import com.mss301.watch.repository.WatchRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

/** Seed đúng dữ liệu trong đề bài (mục 2 - Data). */
// [TODO-6.16: seed đúng nguyên văn đề bài]
@Component
@RequiredArgsConstructor
@Slf4j
public class DataInitializer implements CommandLineRunner {

    private final WatchRepository watchRepository;
    private final WatchCategoryRepository categoryRepository;

    @Override
    public void run(String... args) {
        if (categoryRepository.count() == 0) {
            List<WatchCategory> categories = List.of(
                category("Dive Watches", "Designed for underwater diving and feature high water resistance.",
                    "Automatic", "$500 - $10,000"),
                category("Chronograph Watches", "Watches with a stopwatch function in addition to the main display.",
                    "Automatic or Quartz", "$300 - $8,000"),
                category("Dress Watches", "Elegant and simple, intended to be worn with formal wear.",
                    "Automatic or Manual", "$400 - $20,000"),
                category("Digital Watches", "Watches with an LCD or LED screen that show time in a digital format.",
                    "Quartz", "$50 - $500"),
                category("Pilot Watches", "Originally designed for aviators, featuring large, easy-to-read dials.",
                    "Automatic", "$700 - $15,000")
            );
            categoryRepository.saveAll(categories);
            log.info("Seeded {} categories", categories.size());
        }

        if (watchRepository.count() == 0) {
            List<WatchCategory> cats = categoryRepository.findAll();
            WatchCategory dive = cats.get(0), chrono = cats.get(1), dress = cats.get(2),
                          digital = cats.get(3), pilot = cats.get(4);

            // Thứ tự lưu quyết định WatchID 1..10 -> phải khớp với BrandWatches seed trong MSBrand
            List<Watch> watches = List.of(
                watch("Submariner Date", dive, 1, "Oystersteel", "Oystersteel", "300 meters", "9550.00", LocalDate.of(2020, 9, 1), 50),
                watch("Speedmaster Moonwatch Professional", chrono, 2, "Stainless Steel", "Stainless Steel", "50 meters", "7200.00", LocalDate.of(2021, 1, 5), 75),
                watch("Presage Cocktail Time", dress, 3, "Stainless Steel", "Leather", "50 meters", "425.00", LocalDate.of(2019, 6, 1), 200),
                watch("G-Shock DW-5600E-1V", digital, 4, "Resin", "Resin", "200 meters", "69.95", LocalDate.of(1996, 6, 12), 500),
                watch("Carrera Calibre Heuer 02", chrono, 5, "Stainless Steel", "Alligator Leather", "100 meters", "5900.00", LocalDate.of(2022, 3, 30), 60),
                watch("Seamaster Diver 300M", dive, 2, "Stainless Steel", "Rubber", "300 meters", "5400.00", LocalDate.of(2018, 2, 15), 120),
                watch("Prospex SPB143", dive, 3, "Stainless Steel", "Stainless Steel", "200 meters", "1200.00", LocalDate.of(2020, 7, 1), 150),
                watch("Daytona", chrono, 1, "Oystersteel", "Oystersteel", "100 meters", "14550.00", LocalDate.of(2016, 3, 16), 30),
                watch("F-91W", digital, 4, "Resin", "Resin", "30 meters", "19.99", LocalDate.of(1989, 1, 1), 1000),
                watch("IWC Pilot's Watch Mark XVIII", pilot, 4, "Stainless Steel", "Leather", "60 meters", "4500.00", LocalDate.of(2016, 1, 18), 80)
            );
            watchRepository.saveAll(watches);
            log.info("Seeded {} watches", watches.size());
        }
    }

    private WatchCategory category(String name, String description, String movement, String priceRange) {
        return WatchCategory.builder().categoryName(name).description(description)
            .movementType(movement).priceRange(priceRange).build();
    }

    private Watch watch(String name, WatchCategory category, int brandId, String caseMaterial, String strap,
                        String water, String price, LocalDate releaseDate, int stock) {
        return Watch.builder().name(name).category(category).brandId(brandId)
            .caseMaterial(caseMaterial).strapMaterial(strap).waterpMaterial(water)
            .price(new BigDecimal(price)).releaseDate(releaseDate).stock(stock).build();
    }
}
```

### TODO-6.17 – `AppConfig`

```java
package com.mss301.watch.config;

import feign.Logger;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Spring Boot tự cấu hình bean tools.jackson.databind.json.JsonMapper (Jackson 3),
 * hỗ trợ sẵn LocalDate/LocalDateTime -> chỉ cần inject, không tự tạo mapper.
 */
// [TODO-6.17: Feign logger; dùng JsonMapper (Jackson 3) do Boot cấu hình]
@Configuration
public class AppConfig {

    /** BASIC: log method, URL, status, thời gian của mỗi lời gọi Feign -> thấy rõ các bước Saga gọi MSBrand. */
    @Bean
    Logger.Level feignLoggerLevel() {
        return Logger.Level.BASIC;
    }
}
```

### 📝 Commit – Bước 6

> Mỗi commit phải **build được** (`mvn -q -DskipTests compile` trong service tương ứng). Thứ tự commit bên dưới đã được sắp để thoả điều này.

```bash
git switch -c feature/ms-watch-saga

git add MSWatch_StudentCode/src/main/java/com/mss301/watch/entity/Watch.java \
        MSWatch_StudentCode/src/main/java/com/mss301/watch/entity/WatchCategory.java \
        MSWatch_StudentCode/src/main/java/com/mss301/watch/repository/WatchRepository.java \
        MSWatch_StudentCode/src/main/java/com/mss301/watch/repository/WatchCategoryRepository.java \
        MSWatch_StudentCode/src/main/java/com/mss301/watch/DataInitializer.java
git commit -m "feat(ms-watch): add watch and category entities with seed data" \
  -m "BrandID is a plain reference: brands live in another service's database." \
  -m "Refs: TODO-6.16"

git add MSWatch_StudentCode/src/main/resources/application.yml \
        MSWatch_StudentCode/src/main/java/com/mss301/watch/config
git commit -m "build(ms-watch): configure feign timeouts and saga properties" \
  -m "Refs: TODO-6.1, TODO-6.17"

git add MSWatch_StudentCode/src/main/java/com/mss301/watch/entity/SagaState.java \
        MSWatch_StudentCode/src/main/java/com/mss301/watch/entity/SagaLog.java \
        MSWatch_StudentCode/src/main/java/com/mss301/watch/repository/SagaStateRepository.java \
        MSWatch_StudentCode/src/main/java/com/mss301/watch/repository/SagaLogRepository.java \
        MSWatch_StudentCode/src/main/java/com/mss301/watch/service/saga/SagaStatus.java \
        MSWatch_StudentCode/src/main/java/com/mss301/watch/service/saga/SagaTracker.java
git commit -m "feat(ms-watch): persist saga state and step logs" \
  -m "Tracker writes in REQUIRES_NEW transactions so logs survive any rollback." \
  -m "Refs: TODO-6.2, TODO-6.3, TODO-6.4"

git add MSWatch_StudentCode/src/main/java/com/mss301/watch/service/WatchLocalService.java \
        MSWatch_StudentCode/src/main/java/com/mss301/watch/service/WatchData.java \
        MSWatch_StudentCode/src/main/java/com/mss301/watch/dto/WatchRequest.java
git commit -m "feat(ms-watch): add local transactions and watch snapshot" \
  -m "Refs: TODO-6.5, TODO-6.6"

git add MSWatch_StudentCode/src/main/java/com/mss301/watch/MSWatchApplication.java \
        MSWatch_StudentCode/src/main/java/com/mss301/watch/client
git commit -m "feat(ms-watch): add feign client for brand internal API" \
  -m "Refs: TODO-6.7"

git add MSWatch_StudentCode/src/main/java/com/mss301/watch/service/saga
git commit -m "feat(ms-watch): implement saga orchestrator with LIFO compensation" \
  -m "Each step is a local transaction; completed steps are compensated in reverse order with retries. DELETE_WATCH is the pivot of the delete saga." \
  -m "Refs: TODO-6.8, TODO-6.9, TODO-6.10, TODO-6.11, TODO-6.12"

git add MSWatch_StudentCode/src/main/java/com/mss301/watch/service/WatchService.java \
        MSWatch_StudentCode/src/main/java/com/mss301/watch/service/SagaResult.java \
        MSWatch_StudentCode/src/main/java/com/mss301/watch/controller \
        MSWatch_StudentCode/src/main/java/com/mss301/watch/dto \
        MSWatch_StudentCode/src/main/java/com/mss301/watch/exception
git commit -m "feat(ms-watch): expose watch CRUD and saga monitoring API" \
  -m "Refs: TODO-6.13, TODO-6.14, TODO-6.15"

# Build pass + checklist xong mới merge
git switch main
git merge --no-ff feature/ms-watch-saga -m "Merge branch 'feature/ms-watch-saga'"
```

---

## Bước 7 – API Gateway

### TODO-7.1, TODO-7.2, TODO-7.6 – Routes, CircuitBreaker, TimeLimiter

```yaml
# [TODO-7.1, TODO-7.2, TODO-7.6: routes, CircuitBreaker, TimeLimiter 15s]
server:
  port: 8080

spring:
  application:
    name: api-gateway
  cloud:
    gateway:
      server:
        webflux:            # route của Gateway server WebFlux: spring.cloud.gateway.server.webflux.routes
          routes:
            - id: account-service
              uri: ${ACCOUNT_SERVICE_URL:http://localhost:8081}
              predicates:
                - Path=/api/auth/**
              filters:
                - name: CircuitBreaker
                  args:
                    name: accountCB
                    fallbackUri: forward:/fallback/account

            - id: brand-service
              uri: ${BRAND_SERVICE_URL:http://localhost:8082}
              predicates:
                - Path=/api/brands/**        # KHÔNG route /internal/** -> API nội bộ của Saga không lộ ra ngoài
              filters:
                - name: CircuitBreaker
                  args:
                    name: brandCB
                    fallbackUri: forward:/fallback/brand

            - id: watch-service
              uri: ${WATCH_SERVICE_URL:http://localhost:8083}
              predicates:
                - Path=/api/watches/**,/api/sagas/**
              filters:
                - name: CircuitBreaker
                  args:
                    name: watchCB
                    fallbackUri: forward:/fallback/watch

jwt:
  secret: ${JWT_SECRET:mss301-watch-management-secret-key-2025-very-long-string}

resilience4j:
  circuitbreaker:
    configs:
      default:
        sliding-window-size: 5
        failure-rate-threshold: 50
        wait-duration-in-open-state: 10s
    instances:
      accountCB:
        base-config: default
      brandCB:
        base-config: default
      watchCB:
        base-config: default
  timelimiter:
    configs:
      default:
        # Saga có thể mất vài giây (compensation retry 3 lần x 1s).
        # Nếu để mặc định 1s, Gateway sẽ trả fallback 503 trong khi Saga ở MSWatch vẫn đang chạy.
        timeout-duration: 15s
    instances:              # khai báo rõ cho từng CB để chắc chắn áp dụng 15s
      accountCB:
        base-config: default
      brandCB:
        base-config: default
      watchCB:
        base-config: default

logging:
  level:
    org.springframework.cloud.gateway: INFO
```

```java
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
```

### TODO-7.3, TODO-7.4, TODO-7.5 – `JwtAuthFilter`

```java
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
```

### 📝 Commit – Bước 7

```bash
git switch -c feature/gateway

git add APIGateway_StudentCode/src/main/resources/application.yml \
        APIGateway_StudentCode/src/main/java/com/mss301/gateway/fallback
git commit -m "feat(gateway): configure routes, circuit breakers and fallback" \
  -m "Internal saga endpoints are intentionally not routed." \
  -m "Refs: TODO-7.1, TODO-7.2, TODO-7.6"

git add APIGateway_StudentCode/src/main/java/com/mss301/gateway/filter
git commit -m "feat(gateway): verify jwt and strip client supplied user headers" \
  -m "Only GET /api/watches is public; downstream services trust X-User-Role set by the gateway only." \
  -m "Refs: TODO-7.3, TODO-7.4, TODO-7.5"

# Build pass + checklist xong mới merge
git switch main
git merge --no-ff feature/gateway -m "Merge branch 'feature/gateway'"
```

---

## Bước 8 – Chạy hệ thống

### TODO-8.1, TODO-8.2

Chạy theo thứ tự MSAccount → MSBrand → MSWatch → APIGateway. Kết quả mong đợi:

```http
GET http://localhost:8082/api/brands/1/watches     → watchIds [1, 8]
GET http://localhost:8080/api/watches              → 10 watch, có categoryName, WatchID giảm dần
```

> Không có commit.

---

## Bước 9 – Kiểm thử

### TODO-9.1 – Postman collection

File `WatchManagement/WatchManagement_Saga.postman_collection.json` (53 request, có assertion). Chạy bằng Collection Runner theo thứ tự; kết quả đúng: **0 failed**.

| Folder | Kiểm chứng |
|---|---|
| 00 | Login admin/staff, lưu token |
| 01 | 401 / 403 / inactive / refresh / giả mạo `X-User-Role` |
| 02 | Validation chặn trước Saga |
| 03 | CREATE thành công, MSBrand +1 |
| 04 | CREATE brand 999 → DELETE_WATCH |
| 05 | CREATE + lỗi sau bước 2 → UNASSIGN_BRAND rồi DELETE_WATCH |
| 06 | UPDATE thành công / brand 999 / lỗi sau bước 2 |
| 07 | DELETE + lỗi sau bước 1 / sau pivot |
| 08 | `/api/sagas` chỉ Admin |

### TODO-9.2 → TODO-9.5

Kết quả mong đợi của từng kịch bản (A–G, MSBrand tắt, compensation thất bại, query đối chiếu) đã ghi đầy đủ ở **mục 6 của `Assignment_Readme.md`**. Khi chấm, đối chiếu ảnh chụp của sinh viên với các bảng đó.

### 📝 Commit – Bước 9

```bash
git switch -c test/saga-proof

git add WatchManagement_Saga.postman_collection.json
git commit -m "test(postman): add collection proving saga completion and compensation" \
  -m "Asserts saga step order and cross-checks brand counts in MSBrand after every scenario." \
  -m "Refs: TODO-9.1"

# Build pass + checklist xong mới merge
git switch main
git merge --no-ff test/saga-proof -m "Merge branch 'test/saga-proof'"
```

---

## Bước 10 – Docker

### TODO-10.1 – Dockerfile (ví dụ MSWatch; 3 service còn lại chỉ khác `EXPOSE`)

```dockerfile
# [TODO-10.1: multi-stage build]
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline -B
COPY src ./src
RUN mvn package -DskipTests

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
EXPOSE 8083
ENTRYPOINT ["java", "-jar", "app.jar"]
```

### TODO-10.1, TODO-10.2, TODO-10.3 – `docker-compose.yml`

```yaml
# [TODO-10.1, TODO-10.2, TODO-10.3: sqlserver + healthcheck, db-init, biến môi trường]
services:
  sqlserver:
    image: mcr.microsoft.com/mssql/server:2022-latest
    environment:
      ACCEPT_EULA: "Y"
      MSSQL_SA_PASSWORD: "${DB_PASSWORD}"
    ports:
      - "1433:1433"
    volumes:
      - sqldata:/var/opt/mssql
    healthcheck:
      # Image 2022 mới dùng mssql-tools18 và cần -C (trust server certificate)
      test: ["CMD-SHELL", "/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P \"$${MSSQL_SA_PASSWORD}\" -C -Q \"SELECT 1\" || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 15

  # Tạo 3 database (Database per Service) trước khi các service khởi động
  db-init:
    image: mcr.microsoft.com/mssql/server:2022-latest
    depends_on:
      sqlserver:
        condition: service_healthy
    environment:
      DB_PASSWORD: "${DB_PASSWORD}"
    entrypoint:
      - /bin/bash
      - -c
      - |
        /opt/mssql-tools18/bin/sqlcmd -S sqlserver -U sa -P "$$DB_PASSWORD" -C -Q "
        IF DB_ID('DBAccount') IS NULL CREATE DATABASE DBAccount;
        IF DB_ID('DBBrand')   IS NULL CREATE DATABASE DBBrand;
        IF DB_ID('DBWatch')   IS NULL CREATE DATABASE DBWatch;"
    restart: "no"

  ms-account:
    build: ./MSAccount_StudentCode
    ports:
      - "8081:8081"
    environment:
      DB_HOST: sqlserver
      DB_PASSWORD: "${DB_PASSWORD}"
      JWT_SECRET: "${JWT_SECRET}"
      JWT_EXPIRATION: "${JWT_EXPIRATION}"
      REFRESH_EXPIRATION: "${REFRESH_EXPIRATION}"
    depends_on:
      db-init:
        condition: service_completed_successfully

  ms-brand:
    build: ./MSBrand_StudentCode
    ports:
      - "8082:8082"
    environment:
      DB_HOST: sqlserver
      DB_PASSWORD: "${DB_PASSWORD}"
    depends_on:
      db-init:
        condition: service_completed_successfully

  ms-watch:
    build: ./MSWatch_StudentCode
    ports:
      - "8083:8083"
    environment:
      DB_HOST: sqlserver
      DB_PASSWORD: "${DB_PASSWORD}"
      BRAND_SERVICE_URL: "http://ms-brand:8082"
      SAGA_FAULT_INJECTION: "${SAGA_FAULT_INJECTION:-true}"   # mặc định true để demo; production: false
    depends_on:
      db-init:
        condition: service_completed_successfully
      ms-brand:
        condition: service_started

  api-gateway:
    build: ./APIGateway_StudentCode
    ports:
      - "8080:8080"
    environment:
      JWT_SECRET: "${JWT_SECRET}"
      ACCOUNT_SERVICE_URL: "http://ms-account:8081"
      BRAND_SERVICE_URL: "http://ms-brand:8082"
      WATCH_SERVICE_URL: "http://ms-watch:8083"
    depends_on:
      - ms-account
      - ms-brand
      - ms-watch

volumes:
  sqldata:
```

### 📝 Commit – Bước 10

```bash
git switch -c chore/docker

git add MSAccount_StudentCode/Dockerfile \
        MSBrand_StudentCode/Dockerfile \
        MSWatch_StudentCode/Dockerfile \
        APIGateway_StudentCode/Dockerfile
git commit -m "build(docker): add multi-stage dockerfiles for all services" \
  -m "Refs: TODO-10.1"

git add docker-compose.yml
git commit -m "build(docker): add compose stack with database initialization" \
  -m "SQL Server becomes healthy first, db-init creates the three databases, then services start." \
  -m "Refs: TODO-10.1, TODO-10.2, TODO-10.3"

# Build pass + checklist xong mới merge
git switch main
git merge --no-ff chore/docker -m "Merge branch 'chore/docker'"
```

---

## Lịch sử commit mẫu

```bash
git log --oneline --graph
```

```
*   Merge branch 'chore/docker'
|\
| * build(docker): add compose stack with database initialization
| * build(docker): add multi-stage dockerfiles for all services
|/
*   Merge branch 'test/saga-proof'
|\
| * test(postman): add collection proving saga completion and compensation
|/
*   Merge branch 'feature/gateway'
|\
| * feat(gateway): verify jwt and strip client supplied user headers
| * feat(gateway): configure routes, circuit breakers and fallback
|/
*   Merge branch 'feature/ms-watch-saga'
|\
| * feat(ms-watch): expose watch CRUD and saga monitoring API
| * feat(ms-watch): implement saga orchestrator with LIFO compensation
| * feat(ms-watch): add feign client for brand internal API
| * feat(ms-watch): add local transactions and watch snapshot
| * feat(ms-watch): persist saga state and step logs
| * build(ms-watch): configure feign timeouts and saga properties
| * feat(ms-watch): add watch and category entities with seed data
|/
*   Merge branch 'feature/ms-brand-participant'
|\
| * feat(ms-brand): add public brand endpoints with watch count
| * feat(ms-brand): expose idempotent internal assign and unassign API
| * feat(ms-brand): add brand and brand-watch entities with seed data
|/
*   Merge branch 'docs/saga-design'
|\
| * docs: add saga design for watch create, update and delete
|/
*   Merge branch 'feature/ms-account'
|\
| * feat(ms-account): implement login and refresh endpoints
| * feat(ms-account): issue access and refresh tokens with jjwt
| * feat(ms-account): add store account entity and seed data
|/
*   Merge branch 'feature/scaffold'
|\
| * chore(config): configure SQL Server datasources and naming strategy
| * build: scaffold watch service and gateway with Spring Cloud 2025.1.3
| * build: scaffold account and brand services on Spring Boot 4.1.1
|/
* chore: initialize repository with gitignore and env template
```

Gắn tag bản nộp:

```bash
git tag -a v1.0.0 -m "Watch Management with saga orchestration"
git push origin main --tags
```

### Kiểm tra nhanh chất lượng commit

```bash
# Subject sai chuẩn (dòng nào in ra là SAI)
git log --format=%s | grep -vE '^(Merge|(feat|fix|refactor|build|test|docs|chore|perf|style|ci)(\([a-z0-9-]+\))?!?: .{1,72}$)'

# Commit thiếu "Refs: TODO"
git log --no-merges --format='%H' | while read h; do git show -s --format=%B $h | grep -q 'Refs: TODO' || git show -s --format='%h %s' $h; done

# Có lỡ commit .env?
git log --all --name-only --format= | grep -x '.env' && echo "!!! .env bị commit"
```

---

## Lỗi thường gặp

| Triệu chứng | Nguyên nhân | Cách sửa |
|---|---|---|
| Gateway trả 404 cho mọi route | Khai báo route sai prefix (`spring.cloud.gateway.routes`, cú pháp trong nhiều tutorial trên mạng) | Dùng `spring.cloud.gateway.server.webflux.routes` |
| `ClassNotFoundException ... com.fasterxml.jackson...` | Copy code dùng Jackson 2 (`ObjectMapper`, `JavaTimeModule`) từ tutorial | Inject `tools.jackson.databind.json.JsonMapper` (Jackson 3) |
| `NoClassDefFoundError` liên quan springdoc khi start | Thêm springdoc 2.x | Dùng springdoc 3.x |
| Postman folder 03 báo count sai | DBWatch và DBBrand không được reset cùng lúc, WatchID lệch | Drop và tạo lại cả 2 DB |
| Tạo watch brand 999 lại trả 201 | Có `@CircuitBreaker` fallback vẫn lưu watch | Xem anti-pattern #1 (Readme mục 2.6) |
| Gateway trả 503 "Watch Service is currently unavailable" dù MSWatch vẫn chạy | TimeLimiter mặc định 1s | `resilience4j.timelimiter.configs.default.timeout-duration: 15s` |
| Header `X-Saga-Fail-After-Step` không có tác dụng | `SAGA_FAULT_INJECTION=false` | Bật lại khi test |
| Getter/setter "cannot find symbol" | Lombok chưa chạy annotation processor | Khai báo `annotationProcessorPaths` trong pom (TODO-1.5); bật *Annotation Processing* trong IntelliJ |

---

## Đáp án câu hỏi vấn đáp

1. **`@Transactional` trên `createWatch()`:** `ASSIGN_BRAND` lỗi → Spring rollback DBWatch nên watch biến mất, nhưng nếu MSBrand đã commit thì DBBrand vẫn giữ link → lệch dữ liệu. `SagaLogs` vẫn còn vì `SagaTracker` ghi bằng `REQUIRES_NEW` (transaction độc lập, đã commit). Đồng thời connection DB bị giữ suốt thời gian gọi mạng.
2. **Thứ tự ngược:** bước sau phụ thuộc kết quả bước trước. Kịch bản C: phải gỡ link ở MSBrand (`UNASSIGN_BRAND`) trước, rồi mới xoá watch; nếu xoá watch trước rồi gỡ link lỗi, MSBrand giữ link tới một watch không tồn tại.
3. **Kịch bản B không gọi `UNASSIGN_BRAND`:** `ASSIGN_BRAND` thất bại nên chưa commit, không nằm trong stack → không có gì để bù trừ.
4. **`DELETE_WATCH` là pivot:** xoá cứng dòng có `IDENTITY` thì không khôi phục đúng `WatchID`. Đặt cuối để mọi bước có thể lỗi (gọi mạng) chạy trước, khi còn bù trừ được. Nếu đảo thứ tự: xoá watch xong mà gỡ link lỗi thì phải "tạo lại" watch với id mới, MSBrand và các tham chiếu khác đều sai.
5. **Idempotent:** retry có thể chạy một compensation 2–3 lần (lần đầu có thể đã thành công nhưng mất response). Không idempotent → cộng/trừ lặp, hoặc lỗi 404 ở lần gọi thứ hai làm Saga kẹt.
6. **ACID:** Saga giữ được Atomicity (theo nghĩa cuối cùng: hoặc xong hết, hoặc bù trừ hết), Consistency cuối cùng và Durability (mỗi bước commit). Mất **Isolation**: trong lúc Saga chạy, client khác có thể thấy watch đã có ở DBWatch nhưng chưa được gán brand.
7. **Read timeout nhưng MSBrand đã commit:** orchestrator tưởng bước lỗi nên không bù trừ bước đó → DBBrand còn link mồ côi. An toàn hơn: push compensation vào stack **trước** khi gọi (vì compensation idempotent, gọi thừa vẫn an toàn), hoặc truy vấn lại trạng thái trước khi quyết định.
8. **Saga kẹt ở `COMPENSATING`:** job `@Scheduled` quét `SagaStates` có `Status = COMPENSATING` (hoặc `EXECUTING` quá X phút), đọc `Payload` (snapshot `before`/`after`) và `SagaLogs` để biết bước nào đã bù trừ, rồi chạy tiếp các compensation còn lại (an toàn nhờ idempotent); quá số lần thì cảnh báo cho admin.
9. **Orchestration vs Choreography:** Orchestration dễ quan sát, dễ debug, phù hợp luồng ngắn/ít service (như bài này). Choreography (Kafka event) giảm coupling, phù hợp nhiều service độc lập, nhưng khó theo dõi luồng tổng thể ("event spaghetti").
10. **Fallback ở MSWatch vs Circuit Breaker ở Gateway:** fallback "lưu watch không qua MSBrand" phá vỡ nhất quán (anti-pattern #1). Ở Gateway, Circuit Breaker chỉ trả lỗi 503 nhanh khi service sập, không ghi dữ liệu → không ảnh hưởng tính nhất quán.
