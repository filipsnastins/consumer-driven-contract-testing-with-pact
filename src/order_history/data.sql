INSERT INTO public.customers(
	id, name)
	VALUES ('ac79f127-e877-4995-8805-5f1be1725e1b', 'John Doe');

INSERT INTO public.orders(
	id, customer_id, order_total, state)
	VALUES ('2ae2d5de-383b-418b-909e-c05ccad4080d', 'ac79f127-e877-4995-8805-5f1be1725e1b', 10099, 'APPROVED');
