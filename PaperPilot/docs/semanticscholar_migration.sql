CREATE DATABASE IF NOT EXISTS papers_app DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE papers_app;

-- 用户表
CREATE TABLE IF NOT EXISTS `user` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` VARCHAR(50) NOT NULL COMMENT '用户名',
  `password` VARCHAR(255) NOT NULL COMMENT '密码（加密存储）',
  `nickname` VARCHAR(50) NULL DEFAULT NULL COMMENT '昵称',
  `avatar` VARCHAR(255) NULL DEFAULT NULL COMMENT '头像URL',
  `gender` ENUM('male', 'female', 'unknown') NULL DEFAULT 'unknown' COMMENT '性别',
  `bio` VARCHAR(500) NULL DEFAULT NULL COMMENT '个人简介',
  `phone` VARCHAR(20) NULL DEFAULT NULL COMMENT '手机号',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC),
  UNIQUE INDEX `phone_UNIQUE` (`phone` ASC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户信息表';

-- 用户令牌表
CREATE TABLE IF NOT EXISTS `user_token` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '令牌ID',
  `user_id` INT UNSIGNED NOT NULL COMMENT '用户ID',
  `token` VARCHAR(255) NOT NULL COMMENT '令牌值',
  `expires_at` TIMESTAMP NOT NULL COMMENT '过期时间',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `token_UNIQUE` (`token` ASC),
  INDEX `fk_user_token_user_idx` (`user_id` ASC),
  CONSTRAINT `fk_user_token_user`
    FOREIGN KEY (`user_id`)
    REFERENCES `user` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户令牌表';

-- 论文分类表（对应 arXiv 的 primary_category，如 cs.CV / cs.LG / cs.CL ...）
CREATE TABLE IF NOT EXISTS `paper_primary_category` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '分类ID',
  `name` VARCHAR(50) NOT NULL COMMENT '分类代码，如 cs.CV',
  `sort_order` INT NOT NULL DEFAULT 0 COMMENT '排序顺序',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `name_UNIQUE` (`name` ASC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='论文分类表';

-- 论文表
CREATE TABLE IF NOT EXISTS `papers` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '论文ID（内部主键）',
  `paper_id` VARCHAR(64) NULL DEFAULT NULL COMMENT 'arXiv 原始论文ID，用于去重（如 2604.26951v1）',
  `title` VARCHAR(500) NOT NULL COMMENT '论文标题',
  `abstract` TEXT NULL DEFAULT NULL COMMENT '论文摘要',
  `pdf_url` VARCHAR(500) NULL DEFAULT NULL COMMENT '论文PDF URL',
  `arxiv_url` VARCHAR(500) NULL DEFAULT NULL COMMENT 'arXiv 页面URL',
  `first_author` VARCHAR(100) NULL DEFAULT NULL COMMENT '第一作者',
  `category_id` INT UNSIGNED NOT NULL COMMENT '分类ID',
  `submitted_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '论文提交时间',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `paper_id_UNIQUE` (`paper_id` ASC),
  INDEX `fk_papers_category_idx` (`category_id` ASC),
  INDEX `idx_submitted_at` (`submitted_at` DESC),
  CONSTRAINT `fk_papers_category`
    FOREIGN KEY (`category_id`)
    REFERENCES `paper_primary_category` (`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='论文表';

-- 相关论文关联表（推荐系统，预留给后续升级）
CREATE TABLE IF NOT EXISTS `related_papers` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `paper_id` INT UNSIGNED NOT NULL COMMENT '论文ID',
  `related_paper_id` INT UNSIGNED NOT NULL COMMENT '相关论文ID',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `paper_related_UNIQUE` (`paper_id` ASC, `related_paper_id` ASC),
  INDEX `fk_related_papers_paper_idx` (`paper_id` ASC),
  INDEX `fk_related_papers_related_idx` (`related_paper_id` ASC),
  CONSTRAINT `fk_related_papers_paper`
    FOREIGN KEY (`paper_id`)
    REFERENCES `papers` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_related_papers_related`
    FOREIGN KEY (`related_paper_id`)
    REFERENCES `papers` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='相关论文关联表';

-- 收藏表
CREATE TABLE IF NOT EXISTS `favorite` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '收藏ID',
  `user_id` INT UNSIGNED NOT NULL COMMENT '用户ID',
  `paper_id` INT UNSIGNED NOT NULL COMMENT '论文ID',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `user_paper_UNIQUE` (`user_id` ASC, `paper_id` ASC),
  INDEX `fk_favorite_user_idx` (`user_id` ASC),
  INDEX `fk_favorite_paper_idx` (`paper_id` ASC),
  CONSTRAINT `fk_favorite_user`
    FOREIGN KEY (`user_id`)
    REFERENCES `user` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_favorite_paper`
    FOREIGN KEY (`paper_id`)
    REFERENCES `papers` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='收藏表';

-- 浏览历史表
CREATE TABLE IF NOT EXISTS `history` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '历史ID',
  `user_id` INT UNSIGNED NOT NULL COMMENT '用户ID',
  `paper_id` INT UNSIGNED NOT NULL COMMENT '论文ID',
  `view_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '浏览时间',
  PRIMARY KEY (`id`),
  INDEX `fk_history_user_idx` (`user_id` ASC),
  INDEX `fk_history_paper_idx` (`paper_id` ASC),
  INDEX `idx_view_time` (`view_time` DESC),
  CONSTRAINT `fk_history_user`
    FOREIGN KEY (`user_id`)
    REFERENCES `user` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_history_paper`
    FOREIGN KEY (`paper_id`)
    REFERENCES `papers` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='浏览历史表';

-- AI聊天记录表（Agent，为后续 RAG 升级预留）
CREATE TABLE IF NOT EXISTS `ai_chat` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '聊天记录ID',
  `user_id` INT UNSIGNED NOT NULL COMMENT '用户ID',
  `message` TEXT NOT NULL COMMENT '用户消息',
  `response` TEXT NULL DEFAULT NULL COMMENT 'AI回复',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  INDEX `fk_ai_chat_user_idx` (`user_id` ASC),
  INDEX `idx_created_at` (`created_at` DESC),
  CONSTRAINT `fk_ai_chat_user`
    FOREIGN KEY (`user_id`)
    REFERENCES `user` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI聊天记录表';

-- 创建测试用户 (username: admin / password: admin123，bcrypt 已加密)
INSERT INTO `user` (`username`, `password`, `nickname`, `gender`, `bio`) VALUES
('admin', '$2b$12$TKevPbXcGL6Q1WdaFKbLhuueBuLfLyhkdk/0ESBvBv7X74.rNwiNm', '测试用户', 'unknown', '这是一个测试账号');

-- 初始化数据：不预先写死分类列表，因为 arXiv 的 primary_category 有上百种（cs.CV, cs.LG, cs.CL ...），
-- import_to_db.py 在导入每一行论文数据时会自动 INSERT IGNORE 新的分类，无需在这里手动列出。
