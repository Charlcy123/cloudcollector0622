'use client'

export default function TestPFanHuTu() {
  return (
    <div className="min-h-screen p-8 bg-white">
      <h1 className="text-4xl font-bold mb-8 text-center">PF频凡胡涂体测试页面</h1>
      
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="p-6 border rounded-lg">
          <h2 className="text-2xl font-bold mb-4">PF频凡胡涂体测试</h2>
          <p className="text-lg mb-4">
            这是一段测试文字，用来检验PF频凡胡涂体是否正确加载。
          </p>
          <p className="text-xl mb-4">
            云彩收集手册 - 捕捉天空中的每一朵云，发现它们的独特故事
          </p>
          <p className="text-2xl font-bold">
            天空太大，云太多，用你的方式，记录它们短暂而浪漫的停留
          </p>
          <p className="text-lg mt-4 text-gray-600">
            PF频凡胡涂体具有独特的手写风格，适合表达轻松随意的氛围。
          </p>
        </div>

        <div className="p-6 border rounded-lg">
          <h3 className="text-xl font-bold mb-4">字体信息检测</h3>
          <div className="space-y-2">
            <p>当前字体族: <span id="font-family" className="font-mono bg-gray-100 px-2 py-1 rounded"></span></p>
            <p>计算样式: <span id="computed-font" className="font-mono bg-gray-100 px-2 py-1 rounded"></span></p>
          </div>
        </div>

        <div className="p-6 border rounded-lg">
          <h3 className="text-xl font-bold mb-4">不同字重测试</h3>
          <div className="space-y-2">
            <p className="font-normal">正常字重: PF频凡胡涂体测试文字</p>
            <p className="font-bold">粗体字重: PF频凡胡涂体测试文字</p>
            <p className="font-light">细体字重: PF频凡胡涂体测试文字</p>
          </div>
        </div>

        <div className="p-6 border rounded-lg">
          <h3 className="text-xl font-bold mb-4">特殊字符测试</h3>
          <div className="space-y-2">
            <p className="text-lg">数字: 0123456789</p>
            <p className="text-lg">英文: ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz</p>
            <p className="text-lg">标点: ！@#￥%……&*（）——+{}|："《》？</p>
            <p className="text-lg">中文: 春夏秋冬，东南西北，上下左右，前后内外</p>
          </div>
        </div>
      </div>

      <script dangerouslySetInnerHTML={{
        __html: `
          window.addEventListener('load', function() {
            const testElement = document.querySelector('h1');
            const computedStyle = window.getComputedStyle(testElement);
            
            document.getElementById('font-family').textContent = computedStyle.fontFamily;
            document.getElementById('computed-font').textContent = computedStyle.font;
            
            console.log('Font Family:', computedStyle.fontFamily);
            console.log('Font:', computedStyle.font);
          });
        `
      }} />
    </div>
  )
} 