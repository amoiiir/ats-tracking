import React from "react";

type PopupProps = {
  display: "center" | "top" | "bottom";
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
};

const Popup = ({ display, isOpen, onClose, children }: PopupProps) => {
  if (!isOpen) return null;

  return (
    <div
      className={`fixed inset-0 flex items-${display} justify-center bg-black bg-opacity-50`}
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg shadow-lg p-6"
        onClick={(e) => e.stopPropagation()}
      >
        {children}
      </div>
    </div>
  );
};

export default Popup;