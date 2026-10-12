TRUNCATE products, categories RESTART IDENTITY;

INSERT INTO categories (name) VALUES ('Мячики'), ('Мышки');

INSERT INTO products (category_id, name, description, price, image) VALUES 
((SELECT id FROM categories WHERE name = 'Мячики'),
	'Мячик с бубенчиком', 'Легкий мячик, внутри звенит бубенчик', 49900, NULL),
((SELECT id FROM categories WHERE name = 'Мячики'), 
	'Мячик-ёжик', 'Резиновый мячик с мягкими шипами', 35000, NULL), 
((SELECT id FROM categories WHERE name = 'Мышки'), 
	'Плюшевая мышка', 'Мягкая мышка с кошачьей мятой', 29900, NULL),
((SELECT id FROM categories WHERE name = 'Мышки'), 
	'Мышка с колокольчиком', 'Легкая Мышка, внутри звенит колокольчик.', 29900, NULL);