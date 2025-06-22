import { Iridescence } from "@/components/ui/iridescence";

const IridescenceDemo = () => {
  return (
    <div className="w-screen h-screen"> 
      <Iridescence
        className="w-full h-full" 
        color={[1.0, 1.0, 1.0]}
        mouseReact={false} 
        amplitude={0.1}
        speed={1.0}
      />
    </div>
  );
};

export { IridescenceDemo }; 