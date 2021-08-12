 function main(params) {
	return { 
	    entries: params.rows.map( (row) => { return { //yet another obj
	        id: row.doc.id,
	        city: row.doc.city,
	        state: row.doc.state,
	        st: row.doc.st,
	        address: row.doc.address,
	        zip: row.doc.zip,
	        lat: row.doc.lat,
	        long: row.doc.long
	    }})
	};
}