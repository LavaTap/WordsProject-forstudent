import path from 'node:path';
import multer from 'multer';

// 1) 存储与校验
const upload = multer({
  storage: multer.diskStorage({
    destination: (req, file, cb) => cb(null, 'uploads/wordlists'),
    filename: (req, file, cb) => {
      const ext = path.extname(file.originalname).toLowerCase();
      cb(null, `${req.user.id}-${Date.now()}${ext}`);
    }
  }),
  limits: { fileSize: 512 * 1024 },
  fileFilter: (req, file, cb) => {
    const ext = path.extname(file.originalname).toLowerCase();
    if (ext === '.txt') cb(null, true);
    else cb(new Error('仅支持 .txt 文件'));
  }
});

// 2) 路由
app.post('/api/wordlist', ensureAuth, upload.single('wordfile'), async (req, res, next) => {
  try {
    // TODO: 将 req.file.path 存到数据库，做用户隔离
    await db.user.update({
    where: { id: req.user.id },
    data: {
        hasCustomVocab: true,
        customVocabPath: req.file.path,
        customVocabUploadedAt: new Date()
    }
    });
    return res.redirect(302, '/'); // 跳首页
  } catch (e) {
    next(e);
  }
});

const uploadRoutes = require('./routes/upload');
app.use('/api', uploadRoutes);
