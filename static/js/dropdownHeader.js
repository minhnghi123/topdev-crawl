      // Danh sách từ khóa
      const keywords = ['Java', 'C++', 'JavaScript', 'UI/UX', 'C#', 'Fresher', 'Python', 'PHP', 'Product Owner'];

      // Chọn phần tử highlight
      const highlightElement = document.getElementById('highlight');

      // Hàm để chọn ngẫu nhiên một từ khóa và thay đổi nội dung
      function updateHighlight() {
        const randomKeyword = keywords[Math.floor(Math.random() * keywords.length)];
        highlightElement.textContent = randomKeyword;
      }

      // Gọi hàm ngay khi trang được tải
      updateHighlight();

      // Tự động thay đổi từ khóa sau mỗi 3 giây (3000ms)
      setInterval(updateHighlight, 3000);

      // Hàm mở dropdown
      function openDropdown(element) {
        const menu = element.querySelector('.dropdown-menu');
        menu.style.display = 'block';
      }

      function closeDropdown(element) {
        const menu = element.querySelector('.dropdown-menu');
        menu.style.display = 'none';
      }
