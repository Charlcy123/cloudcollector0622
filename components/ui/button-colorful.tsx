import { cn } from "@/lib/utils";
import { ArrowUpRight } from "lucide-react";

interface ButtonColorfulProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    label?: string;
}

export function ButtonColorful({
    className,
    label = "Explore Components",
    ...props
}: ButtonColorfulProps) {
    return (
        <button
            style={{
                background: 'linear-gradient(to right, #6366f1, #8b5cf6, #ec4899)',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                padding: '8px 16px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer',
                position: 'relative',
                overflow: 'hidden',
                transition: 'all 0.3s ease',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                height: '40px',
            }}
            className={cn(
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/50 focus-visible:ring-offset-2",
                "disabled:pointer-events-none disabled:opacity-50",
                "group",
                className
            )}
            onMouseEnter={(e) => {
                e.currentTarget.style.background = 'linear-gradient(to right, #4f46e5, #7c3aed, #db2777)';
                e.currentTarget.style.transform = 'scale(1.05)';
            }}
            onMouseLeave={(e) => {
                e.currentTarget.style.background = 'linear-gradient(to right, #6366f1, #8b5cf6, #ec4899)';
                e.currentTarget.style.transform = 'scale(1)';
            }}
            {...props}
        >
            {/* 内侧高光效果 */}
            <div
                style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'linear-gradient(to bottom, rgba(255, 255, 255, 0.2), transparent)',
                    borderRadius: '6px',
                    pointerEvents: 'none',
                }}
            />

            {/* Content */}
            <span style={{ position: 'relative', zIndex: 10 }}>{label}</span>
            <ArrowUpRight 
                style={{ 
                    position: 'relative', 
                    zIndex: 10, 
                    width: '14px', 
                    height: '14px',
                    transition: 'transform 0.3s ease'
                }} 
                className="group-hover:rotate-12 group-hover:scale-110" 
            />
        </button>
    );
} 