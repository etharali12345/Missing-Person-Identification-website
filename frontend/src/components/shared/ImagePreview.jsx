import { useState, useRef, useEffect } from "react";
import { ImageUp } from "lucide-react";
import "./imagePreview.css";

export const ImagePreview = ({ image, setImage, isMissing = true }) => {
  const [previewUrl, setPreviewUrl] = useState(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (!image) {
      setPreviewUrl(null);
      return;
    }
    if (typeof image === "string") {
      setPreviewUrl(image);
    } else if (image instanceof File) {
      const url = URL.createObjectURL(image);
      setPreviewUrl(url);
      return () => URL.revokeObjectURL(url);
    }
  }, [image]);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
    }
    e.target.value = "";
  };

  const handleContainerClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <>
      <div
        onClick={handleContainerClick}
        className={`imagePreview-container upload-icon-area ${previewUrl ? "state-has-image" : "state-empty"}`}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="image/jpeg, image/png, image/webp"
          style={{ display: "none" }}
        />

        {!previewUrl ? (
          <div className="text-center p-4">
            <div className="upload-icon-container">
              <ImageUp size={50} strokeWidth={1.7} className="image-icon" />
            </div>
            {isMissing ? (
              <p className="upload-text">اضغط هنا لرفع صورة المفقود</p>
            ) : (
              <p className="upload-text">اضغط هنا لرفع صورة المعثور عليه</p>
            )}
          </div>
        ) : (
          <div className="w-100 h-100 position-relative">
            <img src={previewUrl} alt="Preview" className="preview-image" />
          </div>
        )}
      </div>
    </>
  );
};
