package fu.de190353.userservice.entity;

/**
 * Vai tro cua user. Luu vao DB duoi dang chuoi (nvarchar) qua @Enumerated(EnumType.STRING).
 */
public enum Role {
    USER,
    CREATOR,
    ADMIN
}
