// routes/criminalRoutes.js
const express = require('express');
const path = require('path');
const router = express.Router();
const multer = require('multer');
const criminalController = require('../controllers/criminalController');

// routes/userRoutes.js
const userController = require('../controllers/userController');

// 🔧 Multer setup
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, './public/images');
  },
  filename: (req, file, cb) => {
    const uniqueName = Date.now() + path.extname(file.originalname);
    cb(null, uniqueName);
  }
});

const upload = multer({ storage });

// 🔗 Routes
router.post('/signup', userController.signup);
router.post('/login', userController.login);
router.post('/add-criminal', upload.single('upload-picture'), criminalController.addCriminal);
router.get('/criminals/:id', criminalController.getCriminalById);

module.exports = router;
