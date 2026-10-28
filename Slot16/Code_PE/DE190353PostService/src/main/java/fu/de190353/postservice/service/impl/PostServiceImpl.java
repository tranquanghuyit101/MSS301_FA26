package fu.de190353.postservice.service.impl;

import com.fasterxml.jackson.databind.ObjectMapper;
import feign.FeignException;
import fu.de190353.postservice.client.UserClient;
import fu.de190353.postservice.common.PostConstants;
import fu.de190353.postservice.dto.*;
import fu.de190353.postservice.entity.Post;
import fu.de190353.postservice.entity.PostStatus;
import fu.de190353.postservice.repository.PostRepository;
import fu.de190353.postservice.service.PostService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.ZoneId;
import java.time.temporal.ChronoUnit;
import java.util.Date;
import java.util.List;

@Service
public class PostServiceImpl implements PostService {

    private final PostRepository postRepository;
    private final UserClient userClient;
    private final ObjectMapper objectMapper;

    public PostServiceImpl(PostRepository postRepository, UserClient userClient, ObjectMapper objectMapper) {
        this.postRepository = postRepository;
        this.userClient = userClient;
        this.objectMapper = objectMapper;
    }

    @Override
    @Transactional
    public ApiResponse createPost(PostDTO dto) {
        // Date validation (status 2 -> 406)
        if (!dto.getEndDate().after(dto.getStartDate())) {
            return ApiResponse.error(2, "endDate must be after startDate");
        }

        // Fetch user from UserService via OpenFeign
        UserDTO user = fetchUser(dto.getUserId());
        if (user == null) {
            return ApiResponse.error(4, "User ID is not found");   // 404
        }
        if (!PostConstants.USER_ACTIVE.equals(user.getStatus())) {
            return ApiResponse.error(5, "User is not ACTIVE for posting"); // 400
        }
        if (dto.getNumberOfPosts() > user.getMaxDailyPosts()) {
            return ApiResponse.error(2, "numberOfPosts must not exceed user's maxDailyPosts"); // 406
        }

        Post p = new Post();
        p.setAdvertiserName(dto.getAdvertiserName());
        p.setAdvertiserEmail(dto.getAdvertiserEmail());
        p.setAdvertiserPhone(dto.getAdvertiserPhone());
        p.setStartDate(dto.getStartDate());
        p.setEndDate(dto.getEndDate());
        p.setNumberOfPosts(dto.getNumberOfPosts());
        p.setUserId(dto.getUserId());
        p.setTotalCost(computeTotal(user.getRatePerPost(), dto.getStartDate(), dto.getEndDate()));
        p.setStatus(PostStatus.SCHEDULED); // default SCHEDULED

        Post saved = postRepository.save(p);
        return ApiResponse.of(1, "Post campaign created successfully", toDTO(saved));
    }

    @Override
    @Transactional
    public ApiResponse updatePost(Long postId, PostDTO dto) {
        Post p = postRepository.findById(postId).orElse(null);
        if (p == null) {
            return ApiResponse.error(4, "Post Id is not found");
        }

        // Validate the EFFECTIVE dates BEFORE touching the managed entity.
        Date effectiveStart = dto.getStartDate() != null ? dto.getStartDate() : p.getStartDate();
        Date effectiveEnd   = dto.getEndDate()   != null ? dto.getEndDate()   : p.getEndDate();
        if (!effectiveEnd.after(effectiveStart)) {
            return ApiResponse.error(2, "endDate must be after startDate");
        }

        // Partial update (safe now that dates are validated)
        if (dto.getAdvertiserName() != null)  p.setAdvertiserName(dto.getAdvertiserName());
        if (dto.getAdvertiserEmail() != null) p.setAdvertiserEmail(dto.getAdvertiserEmail());
        if (dto.getAdvertiserPhone() != null) p.setAdvertiserPhone(dto.getAdvertiserPhone());
        p.setStartDate(effectiveStart);
        p.setEndDate(effectiveEnd);
        if (dto.getNumberOfPosts() != null) p.setNumberOfPosts(dto.getNumberOfPosts());
        if (dto.getStatus() != null) p.setStatus(PostStatus.valueOf(dto.getStatus()));

        // Recompute total cost based on the current user rate
        UserDTO user = fetchUser(p.getUserId());
        if (user != null) {
            p.setTotalCost(computeTotal(user.getRatePerPost(), p.getStartDate(), p.getEndDate()));
        }

        Post saved = postRepository.save(p);
        return ApiResponse.ok("Post campaign updated successfully", toDTO(saved));
    }

    @Override
    @Transactional(readOnly = true)
    public ApiResponse getPostById(Long postId) {
        Post p = postRepository.findById(postId).orElse(null);
        if (p == null) {
            return ApiResponse.error(4, "Post is not found");
        }
        return ApiResponse.ok("Successful", toDetailDTO(p));
    }

    @Override
    @Transactional
    public ApiResponse cancelPost(Long postId) {
        Post p = postRepository.findById(postId).orElse(null);
        if (p == null) {
            return ApiResponse.error(4, "Post is not found");
        }
        p.setStatus(PostStatus.CANCELLED);
        postRepository.save(p);
        return ApiResponse.ok("Post campaign is cancelled successfully", null);
    }

    @Override
    @Transactional(readOnly = true)
    public ApiResponse getPostList(String advertiserName, String status, Pageable pageable) {
        Page<Post> page = postRepository.search(emptyToNull(advertiserName), parsePostStatus(status), pageable);
        List<PostDetailDTO> content = page.getContent().stream().map(this::toDetailDTO).toList();

        PageDTO pageDTO = new PageDTO(
                page.getSize(), page.getNumber(), page.getTotalPages(),
                page.getTotalElements(), page.isFirst(), page.isLast(), content);
        return ApiResponse.ok("Successful", pageDTO);
    }

    // -- helpers --

    /** Goi UserService qua OpenFeign; tra null khi user khong ton tai (HTTP 404). */
    private UserDTO fetchUser(Long userId) {
        try {
            ApiResponse res = userClient.getUserById(userId);
            if (res == null || res.getStatus() != 1 || res.getData() == null) {
                return null;
            }
            return objectMapper.convertValue(res.getData(), UserDTO.class);
        } catch (FeignException.NotFound ex) {
            // 404 tu UserService -> coi nhu khong tim thay user (status 4)
            return null;
        }
    }

    private BigDecimal computeTotal(BigDecimal ratePerPost, Date start, Date end) {
        long days = ChronoUnit.DAYS.between(toLocalDate(start), toLocalDate(end));
        if (days < 1) days = 1;
        return ratePerPost.multiply(BigDecimal.valueOf(days));
    }

    private java.time.LocalDate toLocalDate(Date date) {
        return date.toInstant().atZone(ZoneId.systemDefault()).toLocalDate();
    }

    private PostDTO toDTO(Post p) {
        PostDTO d = new PostDTO();
        d.setPostId(p.getPostId());
        d.setAdvertiserName(p.getAdvertiserName());
        d.setAdvertiserEmail(p.getAdvertiserEmail());
        d.setAdvertiserPhone(p.getAdvertiserPhone());
        d.setStartDate(p.getStartDate());
        d.setEndDate(p.getEndDate());
        d.setNumberOfPosts(p.getNumberOfPosts());
        d.setTotalCost(p.getTotalCost());
        d.setStatus(p.getStatus().name());
        d.setUserId(p.getUserId());
        return d;
    }

    private PostDetailDTO toDetailDTO(Post p) {
        PostDetailDTO d = new PostDetailDTO();
        d.setPostId(p.getPostId());
        d.setAdvertiserName(p.getAdvertiserName());
        d.setAdvertiserEmail(p.getAdvertiserEmail());
        d.setAdvertiserPhone(p.getAdvertiserPhone());
        d.setStartDate(p.getStartDate());
        d.setEndDate(p.getEndDate());
        d.setNumberOfPosts(p.getNumberOfPosts());
        d.setTotalCost(p.getTotalCost());
        d.setStatus(p.getStatus().name());
        d.setUser(fetchUser(p.getUserId())); // may be null if user removed
        return d;
    }

    private String emptyToNull(String s) {
        return (s == null || s.isBlank()) ? null : s;
    }

    // Parse filter string -> enum; tra null neu rong/khong hop le (bo qua filter)
    private PostStatus parsePostStatus(String s) {
        if (s == null || s.isBlank()) return null;
        try { return PostStatus.valueOf(s); } catch (IllegalArgumentException e) { return null; }
    }
}
