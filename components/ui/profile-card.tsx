import React, { useEffect, useRef, useCallback, useMemo, useState } from "react";

const DEFAULT_BEHIND_GRADIENT =
  "radial-gradient(farthest-side circle at var(--pointer-x) var(--pointer-y),hsla(266,100%,90%,var(--card-opacity)) 4%,hsla(266,50%,80%,calc(var(--card-opacity)*0.75)) 10%,hsla(266,25%,70%,calc(var(--card-opacity)*0.5)) 50%,hsla(266,0%,60%,0) 100%),radial-gradient(35% 52% at 55% 20%,#00ffaac4 0%,#073aff00 100%),radial-gradient(100% 100% at 50% 50%,#00c1ffff 1%,#073aff00 76%),conic-gradient(from 124deg at 50% 50%,#c137ffff 0%,#07c6ffff 40%,#07c6ffff 60%,#c137ffff 100%)";

const DEFAULT_INNER_GRADIENT =
  "linear-gradient(145deg,#60496e8c 0%,#71C4FF44 100%)";

const ANIMATION_CONFIG = {
  SMOOTH_DURATION: 600,
  INITIAL_DURATION: 1500,
  INITIAL_X_OFFSET: 70,
  INITIAL_Y_OFFSET: 60,
};

const clamp = (value: number, min = 0, max = 100): number =>
  Math.min(Math.max(value, min), max);

const round = (value: number, precision = 3): number =>
  parseFloat(value.toFixed(precision));

const adjust = (
  value: number,
  fromMin: number,
  fromMax: number,
  toMin: number,
  toMax: number
): number =>
  round(toMin + ((toMax - toMin) * (value - fromMin)) / (fromMax - fromMin));

const easeInOutCubic = (x: number): number =>
  x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;

// 内联样式对象
const styles = {
  cardWrapper: {
    position: 'relative' as const,
    width: '100%',
    height: '100%',
    perspective: '1000px',
    transformStyle: 'preserve-3d' as const,
  },
  card: {
    position: 'relative' as const,
    width: '100%',
    height: '100%',
    borderRadius: '16px',
    overflow: 'hidden',
    transformStyle: 'preserve-3d' as const,
    transition: 'transform 0.3s ease-out, box-shadow 0.3s ease',
    cursor: 'pointer',
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(10px)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
  },
  cardActive: {
    boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.1)',
  },
  inside: {
    position: 'relative' as const,
    width: '100%',
    height: '100%',
    borderRadius: 'inherit',
    zIndex: 2,
    overflow: 'hidden',
  },
  shine: {
    position: 'absolute' as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    opacity: 0,
    transition: 'opacity 0.3s ease',
    borderRadius: 'inherit',
    zIndex: 3,
    pointerEvents: 'none' as const,
  },
  glare: {
    position: 'absolute' as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'linear-gradient(135deg, transparent 40%, rgba(255, 255, 255, 0.1) 50%, transparent 60%)',
    opacity: 0,
    transition: 'opacity 0.3s ease, transform 0.6s ease',
    borderRadius: 'inherit',
    zIndex: 4,
    pointerEvents: 'none' as const,
    transform: 'translateX(-100%)',
  },
  content: {
    position: 'relative' as const,
    width: '100%',
    height: '100%',
    padding: '20px',
    display: 'flex',
    flexDirection: 'column' as const,
    justifyContent: 'space-between',
    zIndex: 5,
  },
  avatarContent: {
    position: 'relative' as const,
    width: '100%',
    height: '100%',
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatar: {
    width: '100%',
    height: '100%',
    objectFit: 'cover' as const,
    borderRadius: '12px',
    transition: 'transform 0.3s ease',
  },
};

interface ProfileCardProps {
  avatarUrl?: string;
  iconUrl?: string;
  grainUrl?: string;
  behindGradient?: string;
  innerGradient?: string;
  showBehindGradient?: boolean;
  className?: string;
  enableTilt?: boolean;
  miniAvatarUrl?: string;
  name?: string;
  title?: string;
  handle?: string;
  status?: string;
  contactText?: string;
  showUserInfo?: boolean;
  onContactClick?: () => void;
  children?: React.ReactNode;
}

const ProfileCardComponent: React.FC<ProfileCardProps> = ({
  avatarUrl = "",
  iconUrl = "",
  grainUrl = "",
  behindGradient,
  innerGradient,
  showBehindGradient = true,
  className = "",
  enableTilt = true,
  miniAvatarUrl,
  name = "云朵",
  title = "美丽的云朵",
  handle = "cloud",
  status = "已收集",
  contactText = "查看",
  showUserInfo = true,
  onContactClick,
  children,
}) => {
  const wrapRef = useRef<HTMLDivElement>(null);
  const cardRef = useRef<HTMLElement>(null);
  const [isActive, setIsActive] = useState(false);

  const animationHandlers = useMemo(() => {
    if (!enableTilt) return null;

    let rafId: number | null = null;

    const updateCardTransform = (
      offsetX: number,
      offsetY: number,
      card: HTMLElement,
      wrap: HTMLDivElement
    ) => {
      const width = card.clientWidth;
      const height = card.clientHeight;

      const percentX = clamp((100 / width) * offsetX);
      const percentY = clamp((100 / height) * offsetY);

      const centerX = percentX - 50;
      const centerY = percentY - 50;

      const properties: Record<string, string> = {
        "--pointer-x": `${percentX}%`,
        "--pointer-y": `${percentY}%`,
        "--background-x": `${adjust(percentX, 0, 100, 35, 65)}%`,
        "--background-y": `${adjust(percentY, 0, 100, 35, 65)}%`,
        "--pointer-from-center": `${clamp(Math.hypot(percentY - 50, percentX - 50) / 50, 0, 1)}`,
        "--pointer-from-top": `${percentY / 100}`,
        "--pointer-from-left": `${percentX / 100}`,
        "--rotate-x": `${round(-(centerX / 5))}deg`,
        "--rotate-y": `${round(centerY / 4)}deg`,
      };

      Object.entries(properties).forEach(([property, value]) => {
        wrap.style.setProperty(property, value);
      });
    };

    const createSmoothAnimation = (
      duration: number,
      startX: number,
      startY: number,
      card: HTMLElement,
      wrap: HTMLDivElement
    ) => {
      const startTime = performance.now();
      const targetX = wrap.clientWidth / 2;
      const targetY = wrap.clientHeight / 2;

      const animationLoop = (currentTime: number) => {
        const elapsed = currentTime - startTime;
        const progress = clamp(elapsed / duration);
        const easedProgress = easeInOutCubic(progress);

        const currentX = adjust(easedProgress, 0, 1, startX, targetX);
        const currentY = adjust(easedProgress, 0, 1, startY, targetY);

        updateCardTransform(currentX, currentY, card, wrap);

        if (progress < 1) {
          rafId = requestAnimationFrame(animationLoop);
        }
      };

      rafId = requestAnimationFrame(animationLoop);
    };

    return {
      updateCardTransform,
      createSmoothAnimation,
      cancelAnimation: () => {
        if (rafId) {
          cancelAnimationFrame(rafId);
          rafId = null;
        }
      },
    };
  }, [enableTilt]);

  const handlePointerMove = useCallback(
    (event: PointerEvent) => {
      const card = cardRef.current;
      const wrap = wrapRef.current;

      if (!card || !wrap || !animationHandlers) return;

      const rect = card.getBoundingClientRect();
      animationHandlers.updateCardTransform(
        event.clientX - rect.left,
        event.clientY - rect.top,
        card,
        wrap
      );
    },
    [animationHandlers]
  );

  const handlePointerEnter = useCallback(() => {
    const card = cardRef.current;
    const wrap = wrapRef.current;

    if (!card || !wrap || !animationHandlers) return;

    animationHandlers.cancelAnimation();
    setIsActive(true);
  }, [animationHandlers]);

  const handlePointerLeave = useCallback(
    (event: PointerEvent) => {
      const card = cardRef.current;
      const wrap = wrapRef.current;

      if (!card || !wrap || !animationHandlers) return;

      const target = event.target as HTMLElement;
      const rect = target.getBoundingClientRect();
      const offsetX = event.clientX - rect.left;
      const offsetY = event.clientY - rect.top;

      animationHandlers.createSmoothAnimation(
        ANIMATION_CONFIG.SMOOTH_DURATION,
        offsetX,
        offsetY,
        card,
        wrap
      );
      setIsActive(false);
    },
    [animationHandlers]
  );

  useEffect(() => {
    if (!enableTilt || !animationHandlers) return;

    const card = cardRef.current;
    const wrap = wrapRef.current;

    if (!card || !wrap) return;

    const pointerMoveHandler = handlePointerMove;
    const pointerEnterHandler = handlePointerEnter;
    const pointerLeaveHandler = handlePointerLeave;

    card.addEventListener("pointerenter", pointerEnterHandler as EventListener);
    card.addEventListener("pointermove", pointerMoveHandler as EventListener);
    card.addEventListener("pointerleave", pointerLeaveHandler as EventListener);

    const initialX = wrap.clientWidth - ANIMATION_CONFIG.INITIAL_X_OFFSET;
    const initialY = ANIMATION_CONFIG.INITIAL_Y_OFFSET;

    animationHandlers.updateCardTransform(initialX, initialY, card, wrap);
    animationHandlers.createSmoothAnimation(
      ANIMATION_CONFIG.INITIAL_DURATION,
      initialX,
      initialY,
      card,
      wrap
    );

    return () => {
      card.removeEventListener("pointerenter", pointerEnterHandler as EventListener);
      card.removeEventListener("pointermove", pointerMoveHandler as EventListener);
      card.removeEventListener("pointerleave", pointerLeaveHandler as EventListener);
      animationHandlers.cancelAnimation();
    };
  }, [
    enableTilt,
    animationHandlers,
    handlePointerMove,
    handlePointerEnter,
    handlePointerLeave,
  ]);

  const cardStyle = useMemo(() => {
    const baseStyle = { ...styles.card };
    
    if (isActive) {
      return {
        ...baseStyle,
        ...styles.cardActive,
        transform: `rotateX(var(--rotate-x, 0deg)) rotateY(var(--rotate-y, 0deg)) scale(1.02)`,
      };
    }
    
    return {
      ...baseStyle,
      transform: `rotateX(var(--rotate-x, 0deg)) rotateY(var(--rotate-y, 0deg))`,
    };
  }, [isActive]);

  const shineStyle = useMemo(() => ({
    ...styles.shine,
    background: `radial-gradient(circle at var(--pointer-x, 50%) var(--pointer-y, 50%), rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.1) 20%, transparent 50%)`,
    opacity: isActive ? 1 : 0,
  }), [isActive]);

  const glareStyle = useMemo(() => ({
    ...styles.glare,
    opacity: isActive ? 1 : 0,
    transform: isActive ? 'translateX(100%)' : 'translateX(-100%)',
  }), [isActive]);

  const avatarStyle = useMemo(() => ({
    ...styles.avatar,
    transform: isActive ? 'scale(1.05)' : 'scale(1)',
  }), [isActive]);

  const wrapperStyle = useMemo(
    () =>
      ({
        ...styles.cardWrapper,
        "--card-opacity": "0.15",
        "--pointer-x": "50%",
        "--pointer-y": "50%",
        "--background-x": "50%",
        "--background-y": "50%",
        "--pointer-from-center": "0",
        "--pointer-from-top": "0",
        "--pointer-from-left": "0",
        "--rotate-x": "0deg",
        "--rotate-y": "0deg",
        "--icon": iconUrl ? `url(${iconUrl})` : "none",
        "--grain": grainUrl ? `url(${grainUrl})` : "none",
        "--behind-gradient": showBehindGradient
          ? (behindGradient ?? DEFAULT_BEHIND_GRADIENT)
          : "none",
        "--inner-gradient": innerGradient ?? DEFAULT_INNER_GRADIENT,
      } as React.CSSProperties),
    [iconUrl, grainUrl, showBehindGradient, behindGradient, innerGradient]
  );

  const handleContactClick = useCallback(() => {
    onContactClick?.();
  }, [onContactClick]);

  return (
    <div
      ref={wrapRef}
      className={className}
      style={wrapperStyle}
    >
      <section ref={cardRef} style={cardStyle}>
        <div style={styles.inside}>
          <div style={shineStyle} />
          <div style={glareStyle} />
          <div style={styles.avatarContent}>
            {avatarUrl && (
              <img
                src={avatarUrl}
                alt={`${name || "Cloud"} avatar`}
                loading="lazy"
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.style.display = "none";
                }}
                style={avatarStyle}
              />
            )}
            {children}
          </div>
        </div>
      </section>
    </div>
  );
};

const ProfileCard = React.memo(ProfileCardComponent);

export default ProfileCard; 