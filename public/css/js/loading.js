document.addEventListener('DOMContentLoaded', () => {
  // 模拟加载完成
  setTimeout(() => {
    const loader = document.getElementById('loading-screen');
    loader.classList.add('fade-out');
    setTimeout(() => {
      loader.style.display = 'none';
      document.getElementById('app').style.display = 'block';
    }, 500); // 与 fadeOut 动画时间一致
  }, 800); // 这里可以改成真实数据加载完成的回调
});

// 页面跳转时显示加载
window.addEventListener('beforeunload', () => {
  document.getElementById('loading-screen').style.display = 'flex';
});
