"use client";

import { motion } from "framer-motion";
import { useState } from "react";

interface HandWrittenTitleProps {
    title?: string;
    subtitle?: string;
}

function HandWrittenTitle({
    title = "Hand Written",
    subtitle = "Optional subtitle",
}: HandWrittenTitleProps) {
    const [isHovered, setIsHovered] = useState(false);

    // 默认静态显示状态
    const defaultState = {
        pathLength: 1,
        opacity: 0.6,
    };

    // 悬停动画效果
    const hoverAnimation = {
        initial: {
            pathLength: 1,
            opacity: 0.6,
        },
        animate: {
            pathLength: [1, 0, 1],
            opacity: [0.6, 0.3, 0.9],
            transition: {
                duration: 2,
                times: [0, 0.3, 1],
                ease: [0.43, 0.13, 0.23, 0.96],
            },
        },
    };

    return (
        <div 
            className="relative w-full max-w-4xl mx-auto py-12 cursor-pointer"
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            <div className="absolute inset-0">
                <motion.svg
                    width="100%"
                    height="100%"
                    viewBox="0 0 1200 400"
                    className="w-full h-full"
                >
                    <title>Cloud Collector</title>
                    <motion.path
                        d="M 950 60 
                           C 1250 200, 1050 320, 600 350
                           C 250 350, 150 320, 150 200
                           C 150 80, 350 50, 600 50
                           C 850 50, 950 120, 950 120"
                        fill="none"
                        strokeWidth="8"
                        stroke="currentColor"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        initial={defaultState}
                        animate={isHovered ? hoverAnimation.animate : defaultState}
                        className="text-slate-600/70 transition-colors duration-300"
                        style={{
                            filter: isHovered ? 'drop-shadow(0 0 8px rgba(100, 116, 139, 0.4))' : 'none'
                        }}
                    />
                </motion.svg>
            </div>
            <div className="relative text-center z-10 flex flex-col items-center justify-center">
                <motion.h1
                    className="text-3xl md:text-5xl text-slate-800 tracking-tighter flex items-center gap-2 font-bold transition-all duration-300"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ 
                        opacity: 1, 
                        y: 0,
                        scale: isHovered ? 1.05 : 1
                    }}
                    transition={{ 
                        delay: 0.5, 
                        duration: 0.8,
                        scale: { duration: 0.3 }
                    }}
                >
                    {title}
                </motion.h1>
                {subtitle && (
                    <motion.p
                        className="text-lg text-slate-600 mt-2 transition-all duration-300"
                        initial={{ opacity: 0 }}
                        animate={{ 
                            opacity: isHovered ? 0.9 : 0.7,
                            y: isHovered ? -2 : 0
                        }}
                        transition={{ 
                            delay: 1, 
                            duration: 0.8,
                            y: { duration: 0.3 },
                            opacity: { duration: 0.3 }
                        }}
                    >
                        {subtitle}
                    </motion.p>
                )}
            </div>
        </div>
    );
}

export { HandWrittenTitle }; 