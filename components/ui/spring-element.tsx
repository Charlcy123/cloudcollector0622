'use client';
 
import * as React from 'react';
import {
  type HTMLMotionProps,
  motion,
  useMotionValue,
  useSpring,
} from 'framer-motion';
import { cn } from '@/lib/utils';
 
const generateSpringPath = (
  x1: number,
  y1: number,
  x2: number,
  y2: number,
  springConfig: {
    coilCount?: number;
    amplitude?: number;
  } = {},
) => {
  const {
    coilCount = 12,
    amplitude = 15,
  } = springConfig;
 
  const dx = x2 - x1;
  const dy = y2 - y1;
  const dist = Math.sqrt(dx * dx + dy * dy);
  
  // 如果距离太小，不显示弹簧
  if (dist < 5) return '';
  
  // 计算单位向量
  const ux = dx / dist;
  const uy = dy / dist;
  
  // 垂直向量
  const perpX = -uy;
  const perpY = ux;
  
  // 弹簧段长度
  const segmentLength = dist / coilCount;
  
  let path = [`M${x1},${y1}`];
  
  for (let i = 1; i < coilCount; i++) {
    // 当前点在直线上的位置
    const t = i / coilCount;
    const centerX = x1 + dx * t;
    const centerY = y1 + dy * t;
    
    // 计算弹簧的振荡
    const oscillation = Math.sin(i * Math.PI) * amplitude;
    
    // 最终点位置
    const springX = centerX + perpX * oscillation;
    const springY = centerY + perpY * oscillation;
    
    path.push(`L${springX},${springY}`);
  }
  
  // 连接到终点
  path.push(`L${x2},${y2}`);
  
  return path.join(' ');
};
 
function useMotionValueValue(mv: any) {
  return React.useSyncExternalStore(
    (callback) => {
      const unsub = mv.on('change', callback);
      return unsub;
    },
    () => mv.get(),
    () => mv.get(),
  );
}
 
type SpringAvatarProps = {
  children: React.ReactElement;
  className?: string;
  springClassName?: string;
  dragElastic?: number;
  springConfig?: { stiffness?: number; damping?: number };
  springPathConfig?: {
    coilCount?: number;
    amplitude?: number;
  };
} & HTMLMotionProps<'div'>;
 
function SpringElement({
  ref,
  children,
  className,
  springClassName,
  dragElastic = 0.2,
  springConfig = { stiffness: 200, damping: 16 },
  springPathConfig = { coilCount: 12, amplitude: 15 },
  ...props
}: SpringAvatarProps) {
  const x = useMotionValue(0);
  const y = useMotionValue(0);
 
  const springX = useSpring(x, {
    stiffness: springConfig.stiffness,
    damping: springConfig.damping,
  });
  const springY = useSpring(y, {
    stiffness: springConfig.stiffness,
    damping: springConfig.damping,
  });
 
  const sx = useMotionValueValue(springX);
  const sy = useMotionValueValue(springY);
 
  const childRef = React.useRef<HTMLDivElement>(null);
  React.useImperativeHandle(ref, () => childRef.current as HTMLDivElement);
  const [center, setCenter] = React.useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = React.useState(false);
 
  React.useLayoutEffect(() => {
    function update() {
      if (childRef.current) {
        const rect = childRef.current.getBoundingClientRect();
        setCenter({
          x: rect.left + rect.width / 2,
          y: rect.top + rect.height / 2,
        });
      }
    }
    update();
    window.addEventListener('resize', update);
    window.addEventListener('scroll', update, true);
    return () => {
      window.removeEventListener('resize', update);
      window.removeEventListener('scroll', update, true);
    };
  }, []);
 
  React.useEffect(() => {
    if (isDragging) {
      document.body.style.cursor = 'grabbing';
    } else {
      document.body.style.cursor = 'default';
    }
  }, [isDragging]);
 
  const path = generateSpringPath(
    center.x,
    center.y,
    center.x + sx,
    center.y + sy,
    springPathConfig,
  );
 
  return (
    <>
      {isDragging && path && (
        <svg
          width="100vw"
          height="100vh"
          className="fixed inset-0 w-screen h-screen pointer-events-none z-40"
          style={{ top: 0, left: 0 }}
        >
          <path
            d={path}
            strokeLinecap="round"
            strokeLinejoin="round"
            className={cn(
              'stroke-2 stroke-white/60 fill-none drop-shadow-sm',
              springClassName,
            )}
          />
        </svg>
      )}
      <motion.div
        ref={childRef}
        className={cn(
          'z-50',
          isDragging ? 'cursor-grabbing' : 'cursor-grab',
          className,
        )}
        style={{
          x: springX,
          y: springY,
        }}
        drag
        dragElastic={dragElastic}
        dragMomentum={false}
        onDragStart={() => {
          setIsDragging(true);
        }}
        onDrag={(_, info) => {
          x.set(info.offset.x);
          y.set(info.offset.y);
        }}
        onDragEnd={() => {
          x.set(0);
          y.set(0);
          setIsDragging(false);
        }}
        {...props}
      >
        {children}
      </motion.div>
    </>
  );
}
 
export { SpringElement }; 