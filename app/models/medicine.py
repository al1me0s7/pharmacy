from app.models.database import Database

class Medicine:
    @staticmethod
    def search(query=None, category=None, manufacturer=None, prescription=None, sort='name', city=None):
        base_sql = '''SELECT m.medicine_id, m.manufacturer_id, m.category_id, m.name, m.description,
                             m.active_substance, m.dosage_form, m.dosage_value, m.price, m.quantity_in_stock,
                             m.expiration_date, m.prescription_required, m.contraindications,
                             m.storage_conditions, m.date_added, m.image, m.composition, m.usage_instructions,
                             c.category_name, mf.manufacturer_name,
                             COALESCE(AVG(r.rating), 0) as avg_rating,
                             COUNT(r.review_id) as review_count
                      FROM medicines m 
                      LEFT JOIN categories c ON m.category_id=c.category_id 
                      LEFT JOIN manufacturers mf ON m.manufacturer_id=mf.manufacturer_id
                      LEFT JOIN reviews r ON m.medicine_id=r.medicine_id'''
        where = []
        params = []

        if city not in (None, "", "None"):
            base_sql += '''
            JOIN inventory i ON i.medicine_id = m.medicine_id
            JOIN pharmacies p ON i.pharmacy_id = p.pharmacy_id
            '''
            where.append('p.city_id = %s')
            params.append(int(city))

        if query:
            where.append("(m.name ILIKE %s OR mf.manufacturer_name ILIKE %s OR m.active_substance ILIKE %s)")
            params.extend([f'%{query}%', f'%{query}%', f'%{query}%'])
        if category:
            where.append('m.category_id = %s')
            params.append(category)
        if manufacturer:
            where.append('m.manufacturer_id = %s')
            params.append(manufacturer)
        if prescription in ('yes', 'no'):
            where.append('m.prescription_required = %s')
            params.append(True if prescription == 'yes' else False)

        if where:
            base_sql += ' WHERE ' + ' AND '.join(where)

        base_sql += '''
            GROUP BY
                m.medicine_id, m.manufacturer_id, m.category_id, m.name, m.description,
                m.active_substance, m.dosage_form, m.dosage_value, m.price, m.quantity_in_stock,
                m.expiration_date, m.prescription_required, m.contraindications,
                m.storage_conditions, m.date_added, m.image, m.composition, m.usage_instructions,
                c.category_name, mf.manufacturer_name
        '''

        if sort == 'price_asc':
            base_sql += ' ORDER BY m.price ASC'
        elif sort == 'price_desc':
            base_sql += ' ORDER BY m.price DESC'
        elif sort == 'rating':
            base_sql += ' ORDER BY avg_rating DESC, review_count DESC'
        else:
            base_sql += ' ORDER BY m.name'

        return Database.fetchall(base_sql, tuple(params) if params else None)

    @staticmethod
    def get_by_id(medicine_id):
        return Database.fetchone(
            '''SELECT m.medicine_id, m.manufacturer_id, m.category_id, m.name, m.description,
                      m.active_substance, m.dosage_form, m.dosage_value, m.price, m.quantity_in_stock,
                      m.expiration_date, m.prescription_required, m.contraindications,
                      m.storage_conditions, m.date_added, m.image, m.composition, m.usage_instructions,
                      COALESCE(AVG(r.rating),0) as avg_rating, COUNT(r.review_id) as review_count
               FROM medicines m
               LEFT JOIN reviews r ON m.medicine_id=r.medicine_id
               WHERE m.medicine_id=%s
               GROUP BY
                   m.medicine_id, m.manufacturer_id, m.category_id, m.name, m.description,
                   m.active_substance, m.dosage_form, m.dosage_value, m.price, m.quantity_in_stock,
                   m.expiration_date, m.prescription_required, m.contraindications,
                   m.storage_conditions, m.date_added, m.image, m.composition, m.usage_instructions''',
            (medicine_id,)
        )

    @staticmethod
    def get_by_ids(ids):
        if len(ids) == 1:
            return Database.fetchall('SELECT * FROM medicines WHERE medicine_id = %s', (ids[0],))
        else:
            return Database.fetchall('SELECT * FROM medicines WHERE medicine_id = ANY(%s)', (ids,))