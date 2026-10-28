package fu.de190353.userservice.entity;

/**
 * Trang thai user. Luu vao DB duoi dang chuoi (nvarchar) qua @Enumerated(EnumType.STRING).
 */
public enum UserStatus {
    ACTIVE,
    SUSPENDED,
    DEACTIVATED
}
