export function InstructionsModal() {
  const instructions = [
    {
      text: "اختر صورة واضحة للوجه، يفضل ان يكون الوجه في اتجاه الامام لا الجانب",
      image: "/images/instructions/faces1.jpg",
    },
    {
      text: "تأكد ان الوجه ظاهر بالكامل دون اي نقص، وانه خال من اي عناصر قد تخفي الملامح مثل النظارات الشمسية او الكمامات",
      image: "/images/instructions/faces2.jpg",
    },
    {
      text: "تجنب الصور المظلمة جدا او الساطعة جدا التي تخفي ملامح الوجه",
      image: "/images/instructions/faces3.jpg",
    },
    {
      text: "اختر صورة بجودة عالية، وتجنب الصور ذات الجودة المنخفضة جدا. كما تجنب ايضا الصور التي تحتوي على فلاتر تغير ملامح الشخص",
      image: "/images/instructions/faces4.jpg",
    },
  ];

  return (
    <div
      className="modal fade"
      id="instructions"
      tabIndex="-1"
      aria-labelledby="instructionsLabel"
      aria-hidden="true"
    >
      <div className="modal-dialog modal-md modal-dialog-centered modal-dialog-scrollable">
        <div className="modal-content">
          <div className="modal-header">
            <h6 className="modal-title fw-bold">
              تعليمات عن صورة الشخص المفقود
            </h6>
          </div>
          <div className="modal-body">
            <ul className="px-5 py-0">
              {instructions.map((item, index) => (
                <li key={index} className="py-3">
                  {item.text}
                  <img
                    src={item.image}
                    alt="instruction face"
                    className="img-fluid"
                  />
                </li>
              ))}
            </ul>
          </div>
          <div className="modal-footer">
            <button
              type="button"
              className="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
        </div>
      </div>
    </div>
  );
}
