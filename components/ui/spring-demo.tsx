import { SpringElement } from "@/components/ui/spring-element";

const SpringDemo = () => {
  return (
    <div className="w-screen h-screen bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center">
      <SpringElement
        springConfig={{ stiffness: 150, damping: 12 }}
        springPathConfig={{ coilCount: 16, amplitude: 30 }}
        dragElastic={0.3}
        className="select-none"
        springClassName="stroke-white/80 stroke-3"
      >
        <div className="text-8xl cursor-grab active:cursor-grabbing">
          ☁️
        </div>
      </SpringElement>
    </div>
  );
};

export { SpringDemo }; 