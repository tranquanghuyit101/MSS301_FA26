package fu.de190353.postservice.controller;

import fu.de190353.postservice.dto.ApiResponse;
import fu.de190353.postservice.dto.PostDTO;
import fu.de190353.postservice.service.PostService;
import jakarta.validation.Valid;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/posts")
public class DE190353PostController {

    private final PostService postService;

    public DE190353PostController(PostService postService) {
        this.postService = postService;
    }

    // 1. Create Post -> 201/1, 406/2, 404/4, 400/5, 500/0
    @PostMapping
    public ResponseEntity<ApiResponse> create(@Valid @RequestBody PostDTO dto, BindingResult br) {
        if (br.hasErrors()) {
            return ResponseEntity.status(HttpStatus.NOT_ACCEPTABLE)
                    .body(ApiResponse.error(2, firstError(br)));
        }
        return map(postService.createPost(dto), HttpStatus.CREATED);
    }

    // 2. Update Post -> 200/1, 406/2, 404/4, 500/0
    @PutMapping("/{postId}")
    public ResponseEntity<ApiResponse> update(@PathVariable Long postId,
                                              @RequestBody PostDTO dto,
                                              BindingResult br) {
        if (br.hasErrors()) {
            return ResponseEntity.status(HttpStatus.NOT_ACCEPTABLE)
                    .body(ApiResponse.error(2, firstError(br)));
        }
        return map(postService.updatePost(postId, dto), HttpStatus.OK);
    }

    // 3. Get Post Detail -> 200/1, 404/4, 500/0
    @GetMapping("/{postId}")
    public ResponseEntity<ApiResponse> getById(@PathVariable Long postId) {
        return map(postService.getPostById(postId), HttpStatus.OK);
    }

    // 4. Cancel Post -> 200/1, 404/4, 500/0
    @DeleteMapping("/{postId}")
    public ResponseEntity<ApiResponse> cancel(@PathVariable Long postId) {
        return map(postService.cancelPost(postId), HttpStatus.OK);
    }

    // 5. Get Post List -> 200/1, 406/2, 500/0
    @GetMapping
    public ResponseEntity<ApiResponse> list(@RequestParam(defaultValue = "0") int page,
                                            @RequestParam(defaultValue = "10") int size,
                                            @RequestParam(required = false) String advertiserName,
                                            @RequestParam(required = false) String status) {
        if (size < 1 || size > 100) {
            return ResponseEntity.status(HttpStatus.NOT_ACCEPTABLE)
                    .body(ApiResponse.error(2, "size must be between 1 and 100"));
        }
        Pageable pageable = PageRequest.of(page, size);
        return map(postService.getPostList(advertiserName, status, pageable), HttpStatus.OK);
    }

    // -- map service status -> HTTP code --
    private ResponseEntity<ApiResponse> map(ApiResponse res, HttpStatus okStatus) {
        return switch (res.getStatus()) {
            case 1 -> ResponseEntity.status(okStatus).body(res);
            case 4 -> ResponseEntity.status(HttpStatus.NOT_FOUND).body(res); // 404
            case 5 -> ResponseEntity.status(HttpStatus.BAD_REQUEST).body(res); // 400 user not active
            case 0 -> ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(res);
            default -> ResponseEntity.status(HttpStatus.NOT_ACCEPTABLE).body(res); // 406 for status 2
        };
    }

    private String firstError(BindingResult br) {
        return br.getAllErrors().isEmpty() ? "Validation failed" : br.getAllErrors().get(0).getDefaultMessage();
    }
}
