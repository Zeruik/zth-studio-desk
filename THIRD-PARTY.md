# Third-party and artwork notices

| Component | Version | License | Primary source |
|---|---|---|---|
| Electron | 38.8.6 | MIT plus bundled Chromium/Node notices | https://github.com/electron/electron |
| Fabric.js | 6.9.0 | MIT | https://github.com/fabricjs/fabric.js |
| PDF.js | 5.4.394 | Apache-2.0 | https://github.com/mozilla/pdf.js |
| JSZip | 3.10.1 | MIT | https://github.com/Stuk/jszip |
| node-qrcode | 1.5.4 | MIT | https://github.com/soldair/node-qrcode |
| jsPDF | 3.0.4 | MIT | https://github.com/parallax/jsPDF |
| Noto Sans SC | Google Fonts variable source | SIL Open Font License | https://github.com/google/fonts/tree/main/ofl/notosanssc |
| NSIS | 3.0.4.1 toolchain | zlib/libpng and component licenses | https://nsis.sourceforge.io/ |

Copies of browser-library license notices are in `app/vendor/licenses/`. Noto's OFL is in `app/assets/fonts/OFL.txt`. The default font is renamed ZTH Sans for local application selection; the underlying OFL license remains unchanged.

The studio and club logos were provided by the user. Their artwork and marks are not relicensed under MIT. Generated workshop/product photography and the gradient app icon were created for this project. No full reference recruitment poster is used as an editable-template background. The geometric editorial template uses original text and shape objects.

The color-removal implementation uses fixed-range color distance and connected flood fill, inspired by the documented behavior of OpenCV floodFill and Photopea's Tolerance/Contiguous controls. It does not copy Photopea source, reverse-engineer its application or include a segmentation model.

Primary references: https://docs.opencv.org/doc/doxygen/html/d7/d1b/group__imgproc__misc.html ; https://www.photopea.com/learn/advanced-selecting ; https://www.canva.com/help/download-file-types/ ; https://developer.android.com/develop/ui/views/layout/webapps/load-local-content
